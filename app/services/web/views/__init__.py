from aiohttp.web_app import Application

from .auth import UsersRegisterView, UserLoginView, RefreshTokenView, RevokeTokenView, LoginByTokenView
from .calls import CallsView
from .records import CallRecordsView
from .permissions import PermissionsView
from .tags import TagsView
from .users import UsersView, UserInfoView
from .websocket import WSView


def setup_router(app: Application):
    app.router.add_view('/api/v1/calls/', CallsView, name='calls')
    app.router.add_view('/api/v1/ws/', WSView, name='ws')
    app.router.add_view('/api/v1/record/', CallRecordsView, name='record')
    app.router.add_view('/api/v1/users/', UsersView, name='users')
    app.router.add_view('/api/v1/users/info/', UserInfoView, name='user_info')
    app.router.add_view('/api/v1/users/register/', UsersRegisterView, name='users_register')
    app.router.add_view('/api/v1/users/login/', UserLoginView, name='users_login')
    app.router.add_view('/api/v1/users/login/token/', UserLoginView, name='login_by_token')
    app.router.add_view('/api/v1/users/refresh_token/', RefreshTokenView, name='refresh_token')
    app.router.add_view('/api/v1/users/revoke_token/', RevokeTokenView, name='revoke_token')
    app.router.add_view('/api/v1/tags/', TagsView, name='tags')
    app.router.add_view('/api/v1/permissions/', PermissionsView, name='permissions')


__all__ = ['CallsView', 'WSView', 'CallRecordsView', 'setup_router']
