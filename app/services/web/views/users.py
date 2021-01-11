from aiohttp import web

from app.api.request import RequestUser, RequestUpdateUser
from app.api.response import ResponseUsers, ResponseUser
from app.consts import Permissions
from app.models import User
from .base import BaseClientAuthView


class UsersView(BaseClientAuthView):
    async def get(self):
        self._check_permission(Permissions.users_view)
        users = await User.all()
        return ResponseUsers(users)

    async def post(self):
        self._check_permission(Permissions.users_edit)
        data = await self.get_json()
        request_model = RequestUser(**data)

        await User.all().filter(id=request_model.id).update(
            is_active=request_model.is_active,
            permissions=request_model.permissions
        )
        return web.json_response({'success': True})


class UserInfoView(BaseClientAuthView):
    async def get(self):
        user = await User.get(id=self.uid)
        return ResponseUser.from_orm(user)

    async def put(self):
        data = await self.get_json()
        request_model = RequestUpdateUser(**data)
        await User.all().filter(id=self.uid).update(
            firts_name=request_model.first_name,
            last_name=request_model.last_name,
        )
        return web.json_response({'success': True})
