from datetime import date, datetime
from typing import List

from tortoise.query_utils import Q

from app.api.request import RequestGetCalls
from app.consts import CallType, CallState
from app.models import Call
from app.utils import get_logger

logger = get_logger('CallsQueries', 'INFO')


def _get_dt(dt):
    if isinstance(dt, date):
        return datetime(dt.year, dt.month, dt.day)
    return dt


class CallsQueries:

    @staticmethod
    async def get_calls(request_model: RequestGetCalls) -> List[Call]:
        query = Call.all().prefetch_related('tags').order_by('-created_at')

        if request_model.offset:
            query = query.offset(request_model.offset)

        if request_model.limit:
            query = query.limit(request_model.limit)

        if not request_model.need_recall and request_model.state:
            query = query.filter(state=request_model.state)

        started_from = _get_dt(request_model.started_from)
        started_to = _get_dt(request_model.started_to)

        if started_from:
            query = query.filter(created_at__gte=started_from)

        if started_to:
            query = query.filter(created_at__lte=started_to)

        if request_model.call_type:
            query = query.filter(call_type=request_model.call_type)

        if request_model.number and len(request_model.number) > 4:
            query = query.filter(
                Q(
                    from_number=request_model.number,
                    request_number=request_model.number,
                    join_type='OR'
                )
            )
        elif request_model.number:
            query = query.filter(
                Q(
                    from_pin=request_model.number,
                    request_pin=request_model.number,
                    join_type='OR'
                )
            )

        logger.info(f'request model: {request_model}', request_model=request_model.dict())

        calls = await query

        logger.info(f'{query.sql()}')

        if request_model.need_recall:
            return CallsQueries.need_recalls(calls)

        return calls

    @staticmethod
    def need_recalls(calls: List[Call]) -> List[Call]:
        processed_numbers = set()
        result = []

        for call in calls:
            if call.call_type not in (CallType.INCOMING, CallType.OUTBOUND):
                continue
            if call.from_number in processed_numbers or call.request_number in processed_numbers:
                continue

            if call.call_type == CallType.INCOMING:
                num = call.from_number
            else:
                num = call.request_number

            processed_numbers.add(num)

            if call.state in (CallState.NOT_CONNECTED, CallState.MISSED):
                result.append(call)

        return result
