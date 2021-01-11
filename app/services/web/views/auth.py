from aiohttp import web

from app.api.request import RequestRegister, RequestAuth, RequestRevokeToken, RequestRefreshToken
from app.api.response import ResponseUser
from app.config import app_config
from app.models import User, Token
from app.services.web.exceptions import UsernameIsUsedException, PasswordIsInvalidException
from .base import BaseView


class UsersRegisterView(BaseView):
    async def post(self):
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

        token = await self._get_tokens(user)

        response = web.json_response(ResponseUser.from_orm(user).json())

        response.set_cookie('access_token', token.access_token, max_age=app_config.jwt.access_token_expire)
        response.set_cookie('refresh_token', token.refresh_token, max_age=app_config.jwt.refresh_token_expire)

        return response


class UserLoginView(BaseView):
    async def post(self):
        data = await self.get_json()
        request_model = RequestAuth(**data)

        user = await User.get(username=request_model.username, is_active=True)

        if not user.is_valid_password(request_model.password):
            raise PasswordIsInvalidException

        response_model = await self._get_tokens(user)
        response = web.json_response(response_model.json())

        response.set_cookie('access_token', response_model.access_token, max_age=app_config.jwt.access_token_expire)
        response.set_cookie('refresh_token', response_model.refresh_token, max_age=app_config.jwt.refresh_token_expire)

        return response


class RefreshTokenView(BaseView):
    async def post(self):
        data = await self.get_json()
        request_model = RequestRefreshToken(**data)
        user = await self._get_user_by_refresh(request_model.refresh_token)
        response_model = await self._get_tokens(user)

        response = web.json_response(response_model.json())

        response.set_cookie('access_token', response_model.access_token, max_age=app_config.jwt.access_token_expire)
        response.set_cookie('refresh_token', response_model.refresh_token, max_age=app_config.jwt.refresh_token_expire)

        return response


class RevokeTokenView(BaseView):
    async def post(self):
        data = await self.get_json()
        request_model = RequestRevokeToken(**data)
        await Token.filter(refresh_token=request_model.refresh_token).delete()

        return web.json_response({'success': True})
