from aiohttp import web

from app.api.request import RequestGetCalls
from app.models import Call
from app.queries import CallsQueries
from app.services.websocket import WSInterface


class CallsView(web.View):
    async def get(self):
        """
    ---
    description: Get list of calls
    tags:
    - call
    produces:
    - application/json
    responses:
        "200":
            description: ok
        "405":
            description: invalid HTTP Method
        """
        request_model = RequestGetCalls(**self.request.query)
        calls = await CallsQueries.get_calls(request_model)

        result = {'result': [i.event_schema() for i in calls]}
        return web.json_response(result)

    async def post(self):
        try:
            data = await self.request.json()
        except Exception as err:
            return web.json_response({'result': '', 'error': f'{err}'}, status=400)

        res = await WSInterface.request(data)
        return web.json_response({'result': res})


class CallRecordsView(web.View):
    async def get(self):
        call_id = self.request.query.get('call_id', '')
        call = await Call.filter(id=call_id).prefetch_related('record').first()

        if call and call.record and call.record.converted:
            return web.FileResponse(call.record.converted)

        return web.HTTPNotFound()
