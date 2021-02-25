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
      parameters:
        - in: query
          name: call_id
          type: string
          required: true
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
        call = await Call.filter(id=call_id).first()

        if not call or not call.record_path:
            return web.HTTPNotFound()

        a_number = call.from_pin or call.from_number
        b_number = f'-{call.request_number}' if call.request_number else ''
        internal_number = f'-{call.request_pin}' if call.request_pin else ''

        file_name = f'{call.created_at.date()}-{a_number}{b_number}{internal_number}'

        return web.FileResponse(
            call.record_path,
            headers={
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename="{file_name}.mp3"'
            }
        )

    async def _get_access_token(self) -> str:
        access = await super(CallRecordsView, self)._get_access_token()

        return access or self.request.query.get('token', '')
