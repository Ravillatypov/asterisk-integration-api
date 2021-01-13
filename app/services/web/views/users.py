from aiohttp import web

from app.api.request import RequestUser, RequestUpdateUser
from app.api.response import ResponseUsers, ResponseUser
from app.consts import Permissions
from app.models import User
from .base import BaseClientAuthView


class UsersView(BaseClientAuthView):
    async def get(self):
        """
      ---
      description: Get list of users
      tags:
        - users
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseUsers'
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

        self._check_permission(Permissions.users_view)
        users = await User.all()
        return ResponseUsers(users)

    async def post(self):
        """
      ---
      description: Update user as admin
      tags:
        - users
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestUser'
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

        self._check_permission(Permissions.users_edit)
        data = await self.get_json()
        request_model = RequestUser(**data)

        await User.all().filter(id=request_model.id).update(
            is_active=request_model.is_active,
            permissions=request_model.permissions
        )
        return self.default_success_response


class UserInfoView(BaseClientAuthView):
    async def get(self):
        """
      ---
      description: Get user info
      tags:
        - users
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseUser'
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

        user = await User.get(id=self.uid)
        return ResponseUser.from_orm(user)

    async def post(self):
        """
      ---
      description: Update user info
      tags:
        - users
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestUpdateUser'
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

        data = await self.get_json()
        request_model = RequestUpdateUser(**data)

        await User.all().filter(id=self.uid).update(
            firts_name=request_model.first_name,
            last_name=request_model.last_name,
        )
        return self.default_success_response
