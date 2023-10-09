from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes
from server.settings import QUORUM_CONTRACT_HOST
import json

class Contract():
    def __init__(self, contract_name):
        self.contract_name = contract_name
        self.position = f"/opt/deployed_contract_{self.contract_name}_{QUORUM_CONTRACT_HOST}.json"
        self.public_key = f"/opt/tm/quorum-{QUORUM_CONTRACT_HOST}-tm/tm.pub"

    def load_abi(self):
        """
        Function that loads an abi from a json file
        :return: The abi
        """
        with open(self.position) as f:
            info_json = json.load(f)
        return info_json["abi"]

    def load_contract_address(self):
        """
        Function that loads a deployed contract's address
        :return: The contract address
        """
        with open(self.position) as f:
            info_json = json.load(f)
        return info_json["contractAddress"]

    def load_account_address(self):
        """
        Function that loads the account address of the contract's deployer
        :return: The web3 account address 
        """
        with open(self.position) as f:
            info_json = json.load(f)
        return info_json["deployerAddress"]

    def load_public_key(self):
        """
        Function that loads the public key of the deployer's address
        :return: The public key
        """
        with open(self.public_key) as f:
            public_key = f.read()
        return public_key
    
    def format_address(self, address):
        """
        Function that correctly formats an address for web3 usage
        :param add: The address before
        :return: The address formatted
        """
        before= "".join(address)
        return Web3.toChecksumAddress(before.lower())

    def format_key(self, pk):
        """
        Function that correctly formats a private key for web3 usage
        :param pk: The private key before
        :return: The private key formatted
        """
        before = "".join(pk)
        return bytes.fromhex(before)

    def transact_quorum(self, provider, contract, key, account, func_name, args, abi, chainid):
        """
        Function that makes a transaction to a private contract
        :param provider: The web3 provider
        :param contract: The contract address
        :param key: The node public key
        :param account: The web3 account address
        :param func_name: The name of the function to be called
        :param args: A list containing the arguments of the function
        :param abi: The abi of the contract
        :param chainid: The network chain id
        :return: The status of the transaction, 1 meaning successful, and the transaction hash
        """
        w3_ = Web3(HTTPProvider(provider))
        w3_.middleware_onion.inject(geth_poa_middleware, layer=0)
        instance = w3_.eth.contract(abi=abi, address=contract)
        func = getattr(instance.functions, func_name)
        tx_hash = func(*args).transact({'from': w3_.eth.accounts[0], 'privateFor':key, 'gas': 12000000})
        tx_receipt = w3_.eth.waitForTransactionReceipt(tx_hash, timeout=120)

        print(tx_hash.hex())
        print(tx_receipt)

        if 'revertReason' in tx_receipt:
            tx_revert_reason = tx_receipt['revertReason']

            tx_revert_reason_decoded = self.decode_revert_tx_reason(provider, tx_revert_reason)
        else:
            tx_revert_reason_decoded = ""
        
        return tx_receipt['status'], tx_hash.hex(), tx_revert_reason_decoded

    def call(self, provider, contract, abi, func_name, args):
        """
        Function to make a call to smart contract function
        """
        _w3 = Web3(HTTPProvider(provider))
        #_w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        entity = _w3.eth.contract(address=contract, abi=abi)
        func = getattr(entity.functions, func_name)
        #output = func(*args).transact({'from': _w3.eth.accounts[0]})
        try:
            output = func(*args).call({'from': _w3.eth.accounts[0]})
        except:
            output = func(*args).call({'from': self.ropsten_account_address})
        return output

    def logs_to_list(self, log_items):
        jsonlogs = {}
        jsonargs = {}
        for key,val in log_items:
            if key == "args":
                for k,z in val.items():
                    if type(z) is bytes:
                        jsonargs[k] = (z.decode('utf-8')).split('\x00')[0]
                    else:
                        jsonargs[k] = z            
                jsonlogs['args'] = [jsonargs]
            elif type(val) is bytes:
                jsonlogs[key] = val.decode('utf-8')
            elif type(val) is HexBytes:
                jsonlogs[key] = val.hex()
            else:
                jsonlogs[key] = val
        return jsonlogs

    def receipt_to_json(self, receipt):
        """
            This function is used to 
            manually create a json out
            of a transacion receipt.
            It is needed because of 
            a bug in Web3.toJSON that
            cannot decode logs[args[]]
            that have bytes.
            
        """
        
        json_receipt = {
            "blockHash": receipt['blockHash'].hex(),
            "blockNumber": receipt['blockNumber'],
            "contractAddress": receipt['contractAddress'],
            "cumulativeGasUsed": receipt['cumulativeGasUsed'],
            "from": receipt['from'],
            "gasUsed": receipt['gasUsed'],
            "isPrivacyMarkerTransaction": receipt['isPrivacyMarkerTransaction'],
            "logs": [],
            "logsBloom": receipt['logsBloom'].hex(),
            "transactionIndex": receipt['transactionIndex'],
            "blockcHash": receipt['blockHash'].hex(),
            "status": receipt['status'],
            "to": receipt['to'],
            "transactionHash": receipt['transactionHash'].hex(),
            "transactionIndex": receipt['transactionIndex']
        }
        logs_json = self.logs_to_list(receipt.logs[0][0].items())
        json_receipt['logs'] = logs_json
        print(json_receipt)
        return json_receipt
        
    def get_receipt(self, provider, tx_hash):
        w3 = Web3(HTTPProvider(provider))
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return receipt

    def decode_logs(self, provider, logs, receipt):
        w3 = Web3(HTTPProvider(provider))
        contract_address = logs['address']
        abi = self.load_abi()        
        contract = w3.eth.contract(contract_address, abi=abi)
        decoded_logs = []
        event_signature = (logs['topics'][0]).hex()
        print(f"event_signature:{event_signature}")
        abi_events = [abi for abi in contract.abi if abi["type"] == "event"]
        print(f"abi_events:{abi_events}")
        for event in abi_events:
        # Get event signature components
            name = event["name"]
            print(f"name: {name}")
            inputs = [param["type"] for param in event["inputs"]]
            inputs = ",".join(inputs)
            # # Hash event signature
            event_signature_text = f"{name}({inputs})"
            event_signature_hex = event_signature_text.encode('utf-8')
            event_signature_hex =   Web3.toHex(Web3.keccak(text=event_signature_text))
            # # Find match between log's event signature and ABI's event signature
            if event_signature == event_signature_hex:
                decoded_logs = contract.events[event["name"]]().processReceipt(receipt)
        print(decoded_logs)
        return decoded_logs
    
    def decode_revert_tx_reason(self, provider, revert_reason_hex):
        w3 = Web3(HTTPProvider(provider))
        revert_reason_str_data = f"0x{revert_reason_hex[-64:]}"

        revert_reason_str = w3.toText(hexstr=revert_reason_str_data)

        try:
            revert_reason_str = revert_reason_str.split('\x00')[0]
        except ValueError:
            pass

        return revert_reason_str


    def send_eth(self, provider, to, value):
        w3 = Web3(HTTPProvider(provider))
        print(provider)
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        tx_hash = w3.eth.send_transaction({
        'to': self.format_address(to),
        'from': w3.eth.accounts[0],
        'value': value
        })

        print(w3.eth.waitForTransactionReceipt(tx_hash.hex()))
        print(w3.eth.get_balance(to))