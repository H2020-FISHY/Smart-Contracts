from server.utils.utils import Contract
from django.conf import settings
from . import celery_app

@celery_app.task(bind=True)
def insert_link(self, event_id, ipfs_file_link):
    """
    Celery task to write to Quorum the IPFS link for a FISHY event/policy
    :param: event_id: The id of the event/policy
    :param: ipfs_file_link: The link to the IPFS file
    :return: The status of the transaction and its hash 
    """
    c = Contract('Handler')

    contract_address = c.load_contract_address()
    contract_address = c.format_address(contract_address)
    print(contract_address)

    account_address = c.load_account_address()
    account_address = c.format_address(account_address)
    print(account_address)

    public_key = c.load_public_key()

    abi = c.load_abi()

    event_id = event_id.encode('utf-8')
    arguments = [event_id, ipfs_file_link] 

    status, tx_hash, tx_revert_reason = c.transact_quorum(settings.QUORUM_URL, 
                                        contract_address, 
                                        public_key.split(), 
                                        account_address, 
                                        "storeLink", 
                                        arguments, 
                                        abi, 
                                        1000)

    return status, tx_hash, tx_revert_reason

@celery_app.task(bind=True)
def get_link(self, event_id):
    """
    Celery task t retreive from Quorum the IPFS link for a FISHY event/policy
    :param: event_id: The id of the event/policy
    :return: The status of the transaction and its hash 
    """
    c = Contract('Handler')

    contract_address = c.load_contract_address()
    contract_address = c.format_address(contract_address)

    abi = c.load_abi()

    event_id = event_id.encode('utf-8')
    arguments = [event_id] 

    response = c.call(settings.QUORUM_URL, 
                                        contract_address, 
                                        abi, 
                                        "getLink", 
                                        arguments)

    return response