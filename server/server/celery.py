import os

import sentry_sdk
from celery import Celery
from celery.signals import celeryd_init
from django.conf import settings
from sentry_sdk.integrations.celery import CeleryIntegration


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
app = Celery('server')
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@celeryd_init.connect
def configure_workers(sender=None, conf=None, **kwargs):
    from django.conf import settings
    if settings.SENTRY_ENVIRONMENT:
        sentry_sdk.init(
            settings.SENTRY_URI,
            traces_sample_rate=0.2,
            integrations=[CeleryIntegration()]
        )