from os.path import isfile

import sentry_sdk
from envparse import env
from sentry_sdk.integrations.sanic import SanicIntegration

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
    sentry_sdk.init(SENTRY_DSN, release=RELEASE, integrations=(SanicIntegration(),))

DB_URL = env.str('DB_URL', default='sqlite://db.sqlite3')
AMI_LOG_PATH = env.str('AMI_LOG_PATH', default='ami.log')

TOKEN = env.str('TOKEN')
NUMBERS_LENGTH = env.int('NUMBERS_LENGTH', default=3) + 1
TRUNK_NUMBERS = env.tuple('TRUNK_NUMBERS', default=tuple())
GROUP_NUMBERS = tuple()
