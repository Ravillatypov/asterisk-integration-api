from aiohttp import web

from app.api.request import RequestUser, RequestUpdateUser
from app.api.response import ResponseUsers
from app.models import User


class UsersView(web.View):
    async def get(self):
        users = await User.all()
        return web.json_response(ResponseUsers(users))

    async def post(self):
        data = await self.request.json()
        request_model = RequestUser(**data)

        await User.all().filter(id=request_model.id).update(
            is_active=request_model.is_active,
            permissions=request_model.permissions
        )
        return web.json_response({'success': True})

    async def put(self):
        data = await self.request.json()
        request_model = RequestUpdateUser(**data)
        await User.all().filter(id=self.request.get('uid')).update(
            firts_name=request_model.first_name,
            last_name=request_model.last_name,
        )
        return web.json_response({'success': True})
