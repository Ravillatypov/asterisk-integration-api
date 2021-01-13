from aiohttp import web

from app.api.request import RequestGetCalls, RequestCallEdit, RequestCallback
from app.api.response import ResponseCallsList
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
      parameters:
        - $ref: '#/components/parameters/RequestGetCalls_state'
        - $ref: '#/components/parameters/RequestGetCalls_need_recall'
        - $ref: '#/components/parameters/RequestGetCalls_started_from'
        - $ref: '#/components/parameters/RequestGetCalls_started_to'
        - $ref: '#/components/parameters/RequestGetCalls_call_type'
        - $ref: '#/components/parameters/RequestGetCalls_limit'
        - $ref: '#/components/parameters/RequestGetCalls_offset'
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

        return ResponseCallsList(calls)

    async def post(self):
        """
      ---
      description: Callback
      tags:
        - call
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestCallback'
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: object
                    properties:
                      request_id:
                        type: string
                      data:
                        $ref: '#/components/schemas/RequestCallback'
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

        self._check_permission(Permissions.calls_create)

        data = await self.get_json()
        request_model = RequestCallback(**data)

        res = await WSInterface.request(request_model.dict())
        return web.json_response({'result': res})

    async def put(self):
        """
      ---
      description: Update call info
      tags:
        - call
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestCallEdit'
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseSuccess'
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
