from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

import jwt
from aiohttp import web
from aiohttp.abc import StreamResponse
from aiohttp_cors import CorsViewMixin, ResourceOptions
from jwt import PyJWTError
from pydantic import ValidationError, BaseModel
from pydantic.main import ModelMetaclass
from tortoise.exceptions import DoesNotExist

from app.api.response import ResponseRefreshAccessToken, ResponseSuccess
from app.config import app_config
from app.consts import Permissions
from app.models import User, Token
from app.services.web.exceptions import DataNotFoundException, ApiException, exception_codes
from app.utils import get_logger


class BaseView(web.View, CorsViewMixin):
    default_success_response = ResponseSuccess()
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    }

    def __init__(self, request):
        self.uid: int = None
        self.permissions: List[Permissions] = []
        self.logger = get_logger('views', 'INFO')

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
        except Exception as e:
            return web.json_response(
                status=500,
                data={'success': False, 'errors': [{'message': str(e)}]}
            )

        if result.__class__ is ModelMetaclass or isinstance(result, BaseModel):
            return web.json_response(text=result.json())

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

        user.refresh_token = refresh
        user.access_token = access

        return ResponseRefreshAccessToken(refresh_token=refresh, access_token=access)

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
        return await super()._iter()

    async def authorize(self):
        if not app_config.jwt.enabled or self.request.method.lower() not in ['get', 'post', 'patch', 'put', 'delete']:
            return

        access = self.request.headers.get(self.header_name, '')

        if not access or not isinstance(access, str):
            raise web.HTTPUnauthorized()

        try:
            payload = jwt.decode(access, app_config.jwt.sig, algorithms=['HS256'])

            if payload.get('type', '') != 'access':
                raise web.HTTPUnauthorized()

            self.uid = payload.get('uid')
            self.permissions = Permissions.get_permissions(payload.get('permissions', []))
        except Exception:
            raise web.HTTPUnauthorized()

    def _check_permission(self, perm: Permissions):
        if app_config.jwt.enabled and perm not in self.permissions:
            raise web.HTTPForbidden()
