from typing import List

from tortoise import Tortoise
from tortoise.query_utils import Q

from app.api.request import RequestGetCalls
from app.consts import CallType
from app.models import Call


class CallsQueries:

    @staticmethod
    async def get_need_recall_numbers() -> List[str]:
        conn = Tortoise.get_connection('default')
        data = await conn.execute_query_dict(f'''
                  SELECT number FROM 
                      (SELECT 
                          CASE 
                            WHEN call_type='{CallType.INCOMING.value}' THEN from_number 
                            WHEN call_type='{CallType.OUTBOUND.value}' THEN request_number 
                            ELSE NULL 
                          END number, 
                          state, 
                          MAX(created_at) max_created 
                      FROM "call" GROUP BY number) AS t 
                  WHERE t.number IS NOT NULL AND 
                        t.state IN ('MISSED', 'NOT_CONNECTED')
        ''')
        return [i.get('number') for i in data]

    @staticmethod
    async def get_calls(request_model: RequestGetCalls) -> List[Call]:
        query = Call.all().order_by('-created_at').offset(request_model.offset).limit(request_model.limit)

        if request_model.need_recall:
            numbers = await CallsQueries.get_need_recall_numbers()
            query = query.filter(Q(from_number__in=numbers, request_number__in=numbers, join_type='OR'))
        elif request_model.state:
            query = query.filter(state=request_model.state)

        query = query.filter(created_at__gte=request_model.started_from)

        if request_model.started_to:
            query = query.filter(created_at__lte=request_model.started_to)

        if request_model.call_type:
            query = query.filter(call_type=request_model.call_type)

        return await query
