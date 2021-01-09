from enum import Enum


class CallType(str, Enum):
    INCOMING = 'INCOMING'
    OUTBOUND = 'OUTBOUND'
    INTERNAL = 'INTERNAL'
    UNKNOWN = 'UNKNOWN'


class CallState(str, Enum):
    NEW = 'NEW'
    END = 'END'
    CONNECTED = 'CONNECTED'
    NOT_CONNECTED = 'NOT_CONNECTED'
    MISSED = 'MISSED'


class IntegrationState(str, Enum):
    NEW = 'NEW'
    END = 'END'
    CONNECTED = 'CONNECTED'
    NOT_CONNECTED = 'NOT_CONNECTED'
    MISSED = 'MISSED'

    NOT_FOUNDED = 'NOT_FOUNDED'
    CONVERTED = 'CONVERTED'
    UPLOADED = 'UPLOADED'
    SYNCED = 'SYNCED'


class Permissions(int, Enum):
    calls_view = 0
    calls_edit = 1

    records_view = 2

    tags_view = 3
    tags_edit = 4
    tags_add = 5

    users_view = 6
    users_edit = 7
    users_add = 8
