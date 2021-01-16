from aiohttp import web

from app.consts import Permissions
from app.models import Call
from .base import BaseClientAuthView


class CallRecordsView(BaseClientAuthView):
    async def get(self):
        """
      ---
      description: Get call record file as mp3
      tags:
        - call_record
      responses:
        '200':
          description: ok
          content:
            application/octet-stream:
              schema:
                type: string
                format: bytes
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
        '404':
          description: Call record not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
      security:
        - jwt: []
        """

        self._check_permission(Permissions.records_view)

        call_id = self.request.query.get('call_id', '')
        call = await Call.filter(id=call_id).prefetch_related('record').first()

        if call and call.record and call.record.converted:
            return web.FileResponse(call.record.converted)

        return web.HTTPNotFound()
