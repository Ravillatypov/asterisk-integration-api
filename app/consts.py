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
