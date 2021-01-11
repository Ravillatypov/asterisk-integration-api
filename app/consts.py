from enum import Enum
from typing import List


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
    calls_create = 2

    records_view = 3

    tags_view = 4
    tags_edit = 5
    tags_add = 6

    users_view = 7
    users_edit = 8
    users_add = 9

    @classmethod
    def get_permissions(cls, permissions: List[int]) -> List['Permissions']:
        result = []

        for perm in permissions:
            try:
                result.append(cls(perm))
            except Exception:
                pass

        return result

    @classmethod
    def all(cls) -> List['Permissions']:
        return [Permissions(v) for _, v in cls.__dict__.values() if isinstance(v, int)]
