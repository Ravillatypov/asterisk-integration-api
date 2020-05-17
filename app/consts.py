from enum import Enum


class CallType(str, Enum):
    INCOMING = 'INCOMING'
    OUTBOUND = 'OUTBOUND'
    INTERNAL = 'INTERNAL'
    UNKNOWN = 'UNKNOWN'


class CallState(str, Enum):
    NEW = 'NEW'
    CONNECTED = 'CONNECTED'
    END = 'END'
    MISSED = 'MISSED'
