import json
import logging
import os
import sys
import asyncio

import aioipfs
from aioipfs.exceptions import IPFSConnectionError, APIError, EndpointNotFoundError

import pika 
from django.conf import settings
from django.core.management import BaseCommand
from django_ethereum_events.models import MonitoredEvent
from server.tasks import insert_link, get_link
from server.models import Handler

log = logging.getLogger(__name__)

global cid
global error_message

class Command(BaseCommand):
    help = 'Parses events from the FISHY components'
    print("Starting RabbitMQ consumer")

    def handle(self, *args, **options):
        try:
            print("Start parsing")
            self.parse()
        except KeyboardInterrupt:
            print('Interrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

    async def add_files(self, file: list):
        host = settings.IPFS_HOST
        port = int(settings.IPFS_PORT)

        try:
            client = aioipfs.AsyncIPFS(host=host, port=port)

            async for added_file in client.add(*file, recursive=False):

                if 'code' in added_file and added_file['code'] == 404:
                    raise EndpointNotFoundError(added_file)
                else:
                    print('Imported file {0}, CID: {1}'.format(
                    added_file['Name'], added_file['Hash']))

            await client.close()

            cid = added_file['Hash']
            error_message = ""
            
            print(f" [x] File was stored in IPFS with CID: {cid}")
        except IPFSConnectionError as e:
            print(f'Cannot connect to IPFS with error: {e}')
            cid = ""
            error_message = e
            await client.close()
        except EndpointNotFoundError as e:
            print(f'Cannot connect to IPFS with error: {e}')
            cid = ""
            error_message = e
            await client.close()

        
        return cid, error_message

    def write_to_ipfs(self, file):
        loop = asyncio.get_event_loop()
        cid = loop.run_until_complete(self.add_files([file]))

        return cid

    def write_to_rabbitmq(self, event_id, type, ipfs_link, tx_hash, error_message):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.SMART_CONTRACTS_RABBITMQ_HOST,
            port=settings.SMART_CONTRACTS_RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.SMART_CONTRACTS_RABBITMQ_USER, settings.SMART_CONTRACTS_RABBITMQ_PASSWORD
            ))
        )

        channel = connection.channel()

        result = channel.exchange_declare(exchange=settings.SMART_CONTRACTS_RABBITMQ_EXCHANGE, exchange_type='direct')
        
        result = {
            'id': event_id,
            'type': type,
            'link': ipfs_link,
            'tx_hash': tx_hash,
            'error_message': error_message 
        }

        print(result)

        channel.basic_publish(exchange=settings.SMART_CONTRACTS_RABBITMQ_EXCHANGE,
                      routing_key=settings.SMART_CONTRACTS_RABBITMQ_ROUTING_KEY_VALIDATE,
                      body=json.dumps(result))

        print(f" [x] Sent result of Smart Contracts Component to RabbitMQ!")

        connection.close()

    def write_to_sacm_routing_key(self, event_id, type, ipfs_link, tx_hash, error_message):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.SMART_CONTRACTS_RABBITMQ_HOST,
            port=settings.SMART_CONTRACTS_RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.SMART_CONTRACTS_RABBITMQ_USER, settings.SMART_CONTRACTS_RABBITMQ_PASSWORD
            ))
        )

        channel = connection.channel()

        result = channel.exchange_declare(exchange=settings.SMART_CONTRACTS_RABBITMQ_EXCHANGE, exchange_type='direct')
        
        result = {
            'id': event_id,
            'type': type,
            'link': ipfs_link,
            'tx_hash': tx_hash,
            'error_message': error_message 
        }

        print(result)

        channel.basic_publish(exchange=settings.SMART_CONTRACTS_RABBITMQ_EXCHANGE,
                      routing_key=settings.SACM_SMART_CONTRACTS_RABBITMQ_ROUTING_KEY,
                      body=json.dumps(result))

        print(f" [x] Sent result of Smart Contracts Component to RabbitMQ!")

        connection.close()

    
    def parse(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.FISHY_RABBITMQ_HOST,
            port=settings.FISHY_RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.FISHY_RABBITMQ_USER, settings.FISHY_RABBITMQ_PASSWORD
            ))
        )
        channel = connection.channel()

        result = channel.queue_declare(queue='', exclusive=True, durable=True)
        connection.queue_name = result.method.queue
        channel.queue_bind(exchange=settings.FISHY_RABBITMQ_EXCHANGE, queue=connection.queue_name, routing_key=settings.FISHY_RABBITMQ_ROUTING_KEY)

        def callback(ch, method, properties, body):
            payload = json.loads(body)
            print(" [x] Received %r" % payload)

            component = payload['details']['report']['source']

            try:
                type = payload['task_type']
            except KeyError:
                print("Event has no task_type!")
            
            try:
                id = payload['details']['id']

                ipfs_file= f"/app/server/ipfs_files/event_{id}.json"
            except KeyError:
                print("Event has no id!")
                error_message = "Event has no id!"
                self.write_to_rabbitmq("", type, "", "", error_message)  
            
            try: 
                with open(ipfs_file, "w") as file:
                    json.dump(payload['details'], file, ensure_ascii=False)
                print(f" [x] Created IPFS file")
            except IOError:
                print('Something went wrong! Cannot create IPFS file!')
                error_message = "Cannot create IPFS file!"
                self.write_to_rabbitmq(id, type, "", "", error_message) 

            response_cid, response_error_message = self.write_to_ipfs(ipfs_file)

            print(f"Cid: {response_cid}, Error: {response_error_message}")

            if response_cid != "" and response_error_message == "":
                ipfs_base_link = settings.IPFS_BASE_LINK 
                ipfs_file_link = f"{ipfs_base_link}/{response_cid}"
                
                print(f"Event id: {id}, IPFS link: {ipfs_file_link}")
                # Check if report/event exists
                result = get_link.delay(id)
                event_link = result.get()
                if event_link != "":
                    print(f"The link for the given id already exist!")
                    type_split = type.split('.')[0]
                    error_message = f'The {type_split} with id {id} already exists!'

                    if component == 'SACM':
                        self.write_to_rabbitmq(id, type, ipfs_file_link, "", error_message)
                        self.write_to_sacm_routing_key(id, type, ipfs_file_link, "", error_message)
                    else:
                        self.write_to_rabbitmq(id, type, ipfs_file_link, "", error_message)
                else:
                    # Save to Quorum
                    result = insert_link.delay(id, ipfs_file_link)
                    status, tx_hash, tx_revert_reason = result.get()   

                    if status == 0:
                        print("Something went wrong! Cannot write to blockchain!")

                        if tx_revert_reason == "":
                            error_message = 'Cannot write to blockchain!'
                        else:
                            error_message = f"Cannot write to blockchain!"
                        if component == 'SACM':
                            self.write_to_rabbitmq(id, type, ipfs_file_link, tx_hash, error_message)
                            self.write_to_sacm_routing_key(id, type, ipfs_file_link, tx_hash, error_message) 
                        else:
                            self.write_to_rabbitmq(id, type, ipfs_file_link, tx_hash, error_message)
                    else: 
                        print(f"Status: {status}, Tx_hash: {tx_hash}")

                        # Retreive from Quorum for validation
                        result = get_link.delay(id)
                        event_link = result.get()

                        print(f"The event with link: {event_link} has been retrieved successfully")

                        handler = Handler(id, event_link)
                        
                        # Save to db
                        handler.save()

                        print(f" [x] File link was stored in Postgres")
                        error_message = ""

                        if component == 'SACM':
                            self.write_to_rabbitmq(id, type, ipfs_file_link, tx_hash, error_message)
                            self.write_to_sacm_routing_key(id, type, ipfs_file_link, tx_hash, error_message) 
                        else:
                            self.write_to_rabbitmq(id, type, ipfs_file_link, tx_hash, error_message)
            else: 
                print('Something went wrong!')
                error_message = 'Cannot save IPFS link!'
                if component == 'SACM':
                    self.write_to_rabbitmq(id, type, "", "", error_message) 
                    self.write_to_sacm_routing_key(id, type, "", "", error_message) 
                else:
                    self.write_to_rabbitmq(id, type, "", "", error_message) 

        print("[x] Starting consuming...")
        channel.basic_consume(queue=connection.queue_name, on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

