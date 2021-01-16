from aiohttp import web

from app.api.request import RequestRegister, RequestAuth, RequestRevokeToken, RequestRefreshToken, RequestAuthByToken
from app.api.response import ResponseUserWithTokens
from app.config import app_config
from app.consts import Permissions
from app.models import User, Token
from app.services.web.exceptions import UsernameIsUsedException, PasswordIsInvalidException
from .base import BaseView


class UsersRegisterView(BaseView):
    async def post(self):
        """
      ---
      description: Register
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestRegister'
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseUserWithTokens'
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
        """

        data = await self.get_json()
        request_model = RequestRegister(**data)

        if await User.filter(username=request_model.username).exists():
            raise UsernameIsUsedException

        user = await User(
            username=request_model.username,
            first_name=request_model.first_name,
            last_name=request_model.last_name,
        )
        user.set_password(request_model.password)
        await user.save()

        await self._get_tokens(user)

        return ResponseUserWithTokens.from_orm(user)


class UserLoginView(BaseView):
    async def post(self):
        """
      ---
      description: User login
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestAuth'
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseRefreshAccessToken'
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
        """

        data = await self.get_json()
        request_model = RequestAuth(**data)

        user = await User.get(username=request_model.username, is_active=True)

        if not user.is_valid_password(request_model.password):
            raise PasswordIsInvalidException

        return await self._get_tokens(user)


class RefreshTokenView(BaseView):
    async def post(self):
        """
      ---
      description: Refresh access token
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestRefreshToken'
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseRefreshAccessToken'
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
        """

        data = await self.get_json()
        request_model = RequestRefreshToken(**data)
        user, perm = await self._get_user_by_refresh(request_model.refresh_token)
        return await self._get_tokens(user, permissions=perm)


class RevokeTokenView(BaseView):
    async def post(self):
        """
      ---
      description: Revoke refresh token
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestRevokeToken'
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
        """

        data = await self.get_json()
        request_model = RequestRevokeToken(**data)
        await Token.filter(refresh_token=request_model.refresh_token).delete()

        return self.default_success_response


class LoginByTokenView(BaseView):
    async def post(self):
        """
      ---
      description: Register
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestAuthByToken'
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseRefreshAccessToken'
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
        """

        data = await self.get_json()
        request_model = RequestAuthByToken(**data)

        if request_model.token == app_config.jwt.admin_token:
            permissions = [i.value for i in Permissions.all()]

        elif request_model.token in app_config.jwt.tokens:
            permissions = app_config.jwt.tokens.get(request_model.token)

        else:
            raise web.HTTPUnauthorized()

        return await self._get_tokens(permissions=permissions)
