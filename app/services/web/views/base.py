from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

import jwt
from aiohttp import web
from aiohttp.abc import StreamResponse
from jwt import ExpiredSignatureError, PyJWTError
from pydantic import ValidationError
from pydantic.main import ModelMetaclass
from tortoise.exceptions import DoesNotExist

from app.api.response import ResponseRefreshAccessToken, ResponseSuccess
from app.config import app_config
from app.consts import Permissions
from app.models import User, Token
from app.services.web.exceptions import DataNotFoundException, ApiException, exception_codes


class BaseView(web.View):
    default_success_response = ResponseSuccess()

    def __init__(self, request):
        self.uid: int = None
        self.permissions: List[Permissions] = []

        super().__init__(request)

    async def _iter(self) -> StreamResponse:
        try:
            result = await super()._iter()
        except ApiException as e:
            return web.json_response(
                status=e.status_code,
                data={
                    'success': False,
                    'errors': [{'message': exception_codes[e.code], 'code': e.code}]
                },
            )
        except ValidationError as e:
            return web.json_response(
                status=400,
                data={'success': False, 'errors': [{'message': e.errors()}]},
            )
        except web.HTTPClientError as e:
            message = exception_codes.get(e.status_code) or getattr(e, 'text', '')

            return web.json_response(
                status=e.status_code,
                data={'success': False, 'errors': [{'message': message}]},
            )
        except DoesNotExist:
            return web.json_response(
                status=404,
                data={
                    'success': False,
                    'errors': [{'message': exception_codes[404], 'code': 404}]
                },
            )
        except PyJWTError:
            return web.json_response(
                status=web.HTTPUnauthorized.status_code,
                data={'success': False, 'errors': [{'message': web.HTTPUnauthorized.text}]},
            )

        if result.__class__ is ModelMetaclass:
            return web.json_response(result.json())

        return result

    async def get_text(self) -> str:
        try:
            return await self.request.text()
        except Exception:
            raise DataNotFoundException

    async def get_json(self) -> dict:
        try:
            data = await self.request.json()
            assert isinstance(data, (dict, list)), data
            return data
        except Exception:
            raise DataNotFoundException

    async def get_post(self, check: bool = True) -> dict:
        try:
            res = await self.request.post()
            data = {**res}

            if check:
                assert data, 'Data not found'

            return data
        except Exception:
            raise DataNotFoundException

    @staticmethod
    async def _get_tokens(
            user: User = None,
            uid: int = None,
            permissions: List[int] = None,
    ) -> ResponseRefreshAccessToken:

        if user:
            uid = user.id
            permissions = user.permissions

        if not permissions:
            raise web.HTTPBadRequest

        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        access_expire = now + timedelta(seconds=app_config.jwt.access_token_expire)
        refresh_expire = now + timedelta(seconds=app_config.jwt.refresh_token_expire)

        access = jwt.encode(
            {
                'uid': uid,
                'permissions': permissions,
                'exp': int(access_expire.timestamp()),
                'type': 'access',
            },
            app_config.jwt.sig,
        )
        refresh = jwt.encode(
            {
                'uid': uid,
                'permissions': permissions,
                'exp': int(refresh_expire.timestamp()),
                'type': 'refresh',
            },
            app_config.jwt.sig,
        )

        await Token.create(
            refresh_token=refresh,
            expired_at=refresh_expire,
            user=user,
        )

        return ResponseRefreshAccessToken(refresh_token=refresh, access_token=access)

    def _set_auth_cookies(self, response: StreamResponse, access: str = None, refresh: str = None) -> StreamResponse:
        access = access or self.request.get('access_token')
        refresh = refresh or self.request.get('refresh_token')

        if not access or not refresh:
            return

        response.set_cookie('access_token', access, max_age=app_config.jwt.access_token_expire)
        response.set_cookie('refresh_token', refresh, max_age=app_config.jwt.refresh_token_expire)

    @staticmethod
    async def _get_user_by_refresh(refresh: str) -> Tuple[Optional[User], List[int]]:
        payload = jwt.decode(refresh, app_config.jwt.sig, algorithms=['HS256'])

        if payload.get('type', '') != 'refresh':
            raise web.HTTPUnauthorized()

        if not await Token.filter(refresh_token=refresh).exists():
            raise web.HTTPUnauthorized()

        await Token.filter(refresh_token=refresh).delete()

        user = None
        if payload.get('uid') is not None:
            user = await User.get(id=payload.get('uid'), is_active=True)

        return user, payload.get('permissions', [])


class BaseClientAuthView(BaseView):
    header_name = 'Authorization'

    async def _iter(self) -> StreamResponse:
        await self.authorize()
        response = await super()._iter()
        self._set_auth_cookies(response)
        return response

    async def authorize(self):
        if not app_config.jwt.enabled:
            return

        access = self.request.headers.get(self.header_name, '') or self.request.cookies.get('access_token')
        refresh = self.request.cookies.get('refresh_token')

        if not access or not isinstance(access, str):
            raise web.HTTPForbidden()

        try:
            payload = jwt.decode(access, app_config.jwt.sig, algorithms=['HS256'])

            if payload.get('type', '') != 'access':
                raise web.HTTPUnauthorized()

            self.uid = payload.get('uid')
            self.permissions = Permissions.get_permissions(payload.get('permissions', []))
        except ExpiredSignatureError:
            user, perm = await self._get_user_by_refresh(refresh)

            if user:
                self.uid = user.id
                self.permissions = Permissions.get_permissions(user.permissions)
            else:
                self.permissions = Permissions.get_permissions(perm)

            token = await self._get_tokens(user, permissions=perm)
            self.request['access_token'] = token.access_token
            self.request['refresh_token'] = token.refresh_token

    def _check_permission(self, perm: Permissions):
        if app_config.jwt.enabled and perm not in self.permissions:
            raise web.HTTPForbidden()
