from app.api.response import ResponsePermissions, ResponsePermission
from app.consts import Permissions
from .base import BaseClientAuthView


class PermissionsView(BaseClientAuthView):
    async def get(self):
        """
      ---
      description: Get permissions
      tags:
        - permissions
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponsePermissions'
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
        - jwt: []
        """

        result = [ResponsePermission.from_orm(i) for i in Permissions.all()]
        return ResponsePermissions(result=result)
