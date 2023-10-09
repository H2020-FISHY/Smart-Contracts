import os
from pathlib import Path
from datetime import timedelta
from distutils.util import strtobool
from celery.beat import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-z5d7i(4(t5(&4(um7rg+g5ro9e#*1*tk&q&y9)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.sites',

    'django_ethereum_events',
    # Project apps
    'server'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

# ==================================
#   POSTGRES SETTINGS
# ==================================
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
db_port = os.getenv('POSTGRES_PORT')
db_host = os.getenv('POSTGRES_HOST')
      
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': user,
        'PASSWORD': password,
        'HOST': db_host,
        'PORT': 5432
    }
}

AUTH_PASSWORD_VALIDATORS = [

]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


SITE_ID = 1

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", default='')
CELERY_RESULT_BACKEND = os.getenv("CELERY_BROKER_URL", default='')

# =================================
#   CELERY BEAT SETTINGS
# =================================
CELERY_TIMEZONE = 'UTC'
CELERYBEAT_SCHEDULE = {
    'ethereum_events': {
        'task': 'django_ethereum_events.tasks.event_listener',
        'schedule': timedelta(seconds=20)
    }
}

# ==================================
#   FISHY RABBITMQ SETTINGS
# ==================================
FISHY_RABBITMQ_USER = os.getenv('FISHY_RABBITMQ_USER', default='')
FISHY_RABBITMQ_PASSWORD = os.getenv('FISHY_RABBITMQ_PASSWORD', default='')
FISHY_RABBITMQ_HOST = os.getenv('FISHY_RABBITMQ_HOST', default='')
FISHY_RABBITMQ_PORT = os.getenv('FISHY_RABBITMQ_PORT', default='')
FISHY_RABBITMQ_EXCHANGE = os.getenv('FISHY_RABBITMQ_EXCHANGE', default='')
FISHY_RABBITMQ_ROUTING_KEY = os.getenv('FISHY_RABBITMQ_ROUTING_KEY', default='')

# ===========================================
#  SMART CONTRACTS RESULTS RABBITMQ SETTINGS
# ===========================================
SMART_CONTRACTS_RABBITMQ_USER = os.getenv('SMART_CONTRACTS_RABBITMQ_USER', default='')
SMART_CONTRACTS_RABBITMQ_PASSWORD = os.getenv('SMART_CONTRACTS_RABBITMQ_PASSWORD', default='')
SMART_CONTRACTS_RABBITMQ_HOST = os.getenv('SMART_CONTRACTS_RABBITMQ_HOST', default='')
SMART_CONTRACTS_RABBITMQ_PORT = os.getenv('SMART_CONTRACTS_RABBITMQ_PORT', default='')
SMART_CONTRACTS_RABBITMQ_EXCHANGE = os.getenv('SMART_CONTRACTS_RABBITMQ_EXCHANGE', default='')
SMART_CONTRACTS_RABBITMQ_ROUTING_KEY_VALIDATE = os.getenv('SMART_CONTRACTS_RABBITMQ_ROUTING_KEY_VALIDATE', default='')
SMART_CONTRACTS_RABBITMQ_ROUTING_KEY_RETRY = os.getenv('SMART_CONTRACTS_RABBITMQ_ROUTING_KEY_RETRY', default='')
SACM_SMART_CONTRACTS_RABBITMQ_ROUTING_KEY = os.getenv('SACM_SMART_CONTRACTS_RABBITMQ_ROUTING_KEY', default='')

# ==================================
#   QUORUM SETTINGS
# ==================================
QUORUM_URL = os.getenv("QUORUM_URL", default='')
QUORUM_CONTRACT_HOST = os.getenv('QUORUM_CONTRACT_HOST', default='')

# ==================================
#   IPFS SETTINGS
# ==================================
IPFS_HOST = os.getenv("IPFS_HOST", default='')
IPFS_PORT = os.getenv("IPFS_PORT", default='')
IPFS_BASE_LINK = os.getenv("IPFS_BASE_LINK", default='')

# =================================
#   ETHEREUM-EVENTS SETTINGS
# =================================
ETHEREUM_POA = bool(strtobool(os.getenv('ETHEREUM_POA', default='True')))
ETHEREUM_NODE_URI = QUORUM_URL
ETHEREUM_GETH_POA = ETHEREUM_POA
ETHEREUM_NODE_SSL = False