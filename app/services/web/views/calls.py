from aiohttp import web

from app.api.request import RequestGetCalls, RequestCallEdit
from app.consts import Permissions
from app.models import Call, Tag
from app.queries import CallsQueries
from app.services.websocket import WSInterface
from .base import BaseClientAuthView


class CallsView(BaseClientAuthView):
    async def get(self):
        """
      ---
      description: Get list of calls
      tags:
        - call
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseCallsList'
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
        '403':
          description: Forbidden
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
      security:
        - jwt
        """

        self._check_permission(Permissions.calls_view)

        request_model = RequestGetCalls(**self.request.query)
        calls = await CallsQueries.get_calls(request_model)

        result = {'result': [i.event_schema() for i in calls]}
        return web.json_response(result)

    async def post(self):
        self._check_permission(Permissions.calls_create)

        data = await self.get_json()

        res = await WSInterface.request(data)
        return web.json_response({'result': res})

    async def put(self):
        self._check_permission(Permissions.calls_edit)
        data = await self.get_json()
        request_model = RequestCallEdit(**data)
        call = await Call.get(id=request_model.id)

        if request_model.comment is not None:
            call.comment = request_model.comment

        if request_model.tags is not None:
            call.tags = await Tag.filter(name__in=request_model.tags)

        await call.save()

        return self.default_success_response


class CallRecordsView(BaseClientAuthView):
    async def get(self):
        self._check_permission(Permissions.records_view)

        call_id = self.request.query.get('call_id', '')
        call = await Call.filter(id=call_id).prefetch_related('record').first()

        if call and call.record and call.record.converted:
            return web.FileResponse(call.record.converted)

        return web.HTTPNotFound()
