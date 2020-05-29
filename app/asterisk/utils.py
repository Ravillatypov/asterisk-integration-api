import re
from typing import Optional

from tortoise.query_utils import Q


from .data_types import CallNumbers
from .. import settings
from ..consts import CallType
from ..models import Call, CallRecord

re._pattern_type = re.Pattern

internal_regexp = re.compile(r'\d{2,4}')
external_regexp = re.compile(r'^(.*?)(\d{5,11})$')
number_regexp = re.compile(r'\d{2,11}')


def is_equal(num1: str, num2: str) -> bool:
    min_length = min(len(num1), len(num2))
    min_length = 10 if min_length > 10 else min_length

    if 0 < min_length < 11:
        return num1[-min_length:] == num2[-min_length:]
    return False


def is_group_numbers(*numbers: str) -> bool:
    for number in numbers:
        if number and number in settings.GROUP_NUMBERS:
            return True
    return False


def is_internal(number: str) -> bool:
    return 0 < len(number) < 5 and internal_regexp.match(number) is not None


def is_external(number: str) -> bool:
    if not number:
        return False
    m = external_regexp.match(number)
    return m is not None and m.group(2)


def get_internal(number: str) -> str:
    m = None
    if 0 < len(number) < 5:
        m = internal_regexp.match(number)
    return m.group() if m else ''


def get_external(number: str) -> str:
    m = None
    if number:
        m = external_regexp.match(number)
    return m.group(2) if m else ''


def get_number(number: str) -> str:
    number = ''.join((i for i in number if i.isdigit()))
    return number


def get_call_type(num: CallNumbers) -> str:
    result = CallType.UNKNOWN

    if not any((num.from_pin, num.from_number, num.request_number, num.request_pin)):
        return result

    elif any((num.from_number and num.from_number in settings.TRUNK_NUMBERS,
              is_internal(num.from_pin) and is_external(num.request_number))):
        result = CallType.OUTBOUND

    elif any((num.request_number and num.request_number in settings.TRUNK_NUMBERS,
              is_external(num.from_number) and is_internal(num.request_pin))):
        result = CallType.INCOMING

    elif is_internal(num.from_pin) and is_internal(num.request_pin):
        result = CallType.INTERNAL

    return result


def validate_numbers(from_num: str, request_num: str) -> CallNumbers:
    return CallNumbers(
        get_internal(from_num),
        get_external(from_num),
        get_external(request_num),
        get_internal(request_num)
    )


async def find_call_record(call: Call) -> Optional[CallRecord]:
    return await CallRecord.filter(
        Q(call=call) |
        Q(call=None, channel__call=call) |
        Q(call=None, channel__bridged__call=call)
    ).first()
