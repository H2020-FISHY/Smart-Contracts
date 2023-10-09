from django.core.management import BaseCommand

from django_ethereum_events.models import MonitoredEvent
from django_ethereum_events.chainevents import AbstractEventReceiver

from server.utils.utils import Contract


c = Contract('Handler')
fishy_sc_abi = c.load_abi()
fishy_sc_address = c.load_contract_address()

class NewEventReceiver(AbstractEventReceiver):
    def save(self, decoded_event):
        print('Received event: {}'.format(decoded_event))

receiver = 'server.management.commands.register_events.NewEventReceiver'

DEFAULT_EVENTS = [
    ('NewLink', fishy_sc_address, fishy_sc_abi, receiver),
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        monitored_events = MonitoredEvent.objects.all()
        for event in DEFAULT_EVENTS:

            if not monitored_events.filter(name=event[0], contract_address__iexact=event[1]).exists():
                self.stdout.write('Creating monitor for event {} at {}'.format(event[0], event[1]))

                MonitoredEvent.objects.register_event(*event)

        self.stdout.write(self.style.SUCCESS('Events are up to date'))