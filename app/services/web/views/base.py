from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple, Awaitable, Type

import jwt
from aiohttp import web
from aiohttp.abc import StreamResponse
from aiohttp_cors import CorsViewMixin, ResourceOptions
from jwt import PyJWTError
from pydantic import ValidationError, BaseModel
from pydantic.main import ModelMetaclass
from tortoise.exceptions import DoesNotExist

from app.api.response import ResponseRefreshAccessToken, ResponseSuccess
from app.config import app_config, AppConfig
from app.consts import Permissions
from app.models import User, Token
from app.services.web.exceptions import DataNotFoundException, ApiException, exception_codes
from app.utils import get_logger

_http_methods = ['get', 'post', 'patch', 'put', 'delete']


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
        self.company_id: int = 0

        super().__init__(request)

    async def _iter(self) -> StreamResponse:
        return await self._view_exception_handler(super(BaseView, self)._iter())

    @staticmethod
    async def _view_exception_handler(coroutine: Awaitable) -> StreamResponse:
        try:
            result = await coroutine
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
            response_cls: Type[BaseModel] = ResponseRefreshAccessToken,
    ):
        company_id = 0

        if user:
            uid = user.id
            permissions = user.permissions
            company_id = user.company_id

        if not permissions:
            raise web.HTTPBadRequest

        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        access_expire = now + timedelta(seconds=app_config.jwt.access_token_expire)
        refresh_expire = now + timedelta(seconds=app_config.jwt.refresh_token_expire)

        access = jwt.encode(
            {
                'uid': uid,
                'permissions': permissions,
                'company_id': company_id,
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

        if user:
            await Token.create(
                refresh_token=refresh,
                expired_at=refresh_expire,
                user=user,
            )
        else:
            user = User()

        user.refresh_token = refresh
        user.access_token = access

        response_model = response_cls.from_orm(user)
        response = web.json_response(response_model.dict())
        response.set_cookie('accessKey', access, max_age=app_config.jwt.access_token_expire)

        return response

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

    @property
    def conf(self) -> AppConfig:
        return app_config


class BaseClientAuthView(BaseView):
    header_name = 'Authorization'
    auth_not_required: Tuple[str] = tuple()

    async def _iter(self) -> StreamResponse:
        return await self._view_exception_handler(self._handler())

    async def _handler(self):
        await self.authorize()
        return await super()._iter()

    async def authorize(self):
        method = self.request.method.lower()
        if not app_config.jwt.enabled or method not in _http_methods or method in self.auth_not_required:
            return

        access = await self._get_access_token()

        if not access or not isinstance(access, str):
            raise web.HTTPUnauthorized()

        try:
            payload = jwt.decode(access, app_config.jwt.sig, algorithms=['HS256'])

            if payload.get('type', '') != 'access':
                raise web.HTTPUnauthorized()

            self.uid = payload.get('uid')
            self.permissions = Permissions.get_permissions(payload.get('permissions', []))
            self.company_id = payload.get('company_id', 0)
        except Exception:
            raise web.HTTPUnauthorized()

    def _check_permission(self, perm: Permissions):
        if app_config.jwt.enabled and perm not in self.permissions:
            self.logger.warning('has not required permissions', permissions=self.permissions, permission=perm)
            raise web.HTTPForbidden()

    async def _get_access_token(self) -> str:
        return self.request.headers.get(self.header_name, '') or self.request.cookies.get('accessKey', '')
