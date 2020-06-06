from os.path import isfile

import sentry_sdk
from envparse import env
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

# Init settings using the .env file
if isfile('.env'):
    env.read_envfile('.env')

ENVIRONMENT = env.str('ENVIRONMENT', default='local')  # local, test, dev, prod
IS_TEST = ENVIRONMENT == 'test'
IS_PROD = ENVIRONMENT == 'prod'
IS_DEV = ENVIRONMENT in ('local', 'dev')

# AMI settings
IP = env.str('IP', default='127.0.0.1')
PORT = env.int('PORT', default=5038)
LOGIN = env.str('LOGIN')
SECRET = env.str('SECRET')

# sentry init
SENTRY_DSN = env.str('SENTRY_DSN', default='')
RELEASE = env.str('RELEASE', default='local')
if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, release=RELEASE, integrations=(AioHttpIntegration(),))

DB_URL = env.str('DB_URL', default='sqlite://db.sqlite3')
AMI_LOG_PATH = env.str('AMI_LOG_PATH', default='ami.log')

DEFAULT_CONTEXT = env.str('DEFAULT_CONTEXT', default='default')
START_DIGIT = env.str('START_DIGIT', default='8')
NUMBERS_LENGTH = env.int('NUMBERS_LENGTH', default=3) + 1
TRUNK_NUMBERS = env.tuple('TRUNK_NUMBERS', default=tuple())
GROUP_NUMBERS = tuple()
CITY_CODES = {len(i): i for i in ('7',) + env.tuple('CITY_CODES', default=tuple())}

RECORDS_IS_ENABLED = env.bool('RECORDS_IS_ENABLED', default=True)
RECORDS_PATH = env.str('RECORDS_PATH', default='/records')
RECORDS_STORE_DAYS = env.int('RECORDS_STORE_DAYS', default=30)
RECORDS_UPLOAD_URL = env.str('RECORDS_UPLOAD_URL', default='')
RECORDS_UPLOAD_HEADERS = env.dict('RECORDS_UPLOAD_HEADERS', default={})
CONVERTED_RECORDS_PATH = env.str('CONVERTED_RECORDS_PATH', default='/records')

WS_URL = env.str('WS_URL', default='')
WS_HEADERS = env.dict('WS_HEADERS', default={})

EVENTS_URL = env.str('EVENTS_URL', default='')
EVENTS_HEADERS = env.dict('EVENTS_HEADERS', default={})
