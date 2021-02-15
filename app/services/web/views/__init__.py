import aiohttp_cors
from aiohttp.web_app import Application

from .ats import AtsInfoView
from .auth import UsersRegisterView, UserLoginView, RefreshTokenView, RevokeTokenView, LoginByTokenView
from .calls import CallsView
from .permissions import PermissionsView
from .records import CallRecordsView
from .tags import TagsView
from .users import UsersView, UserInfoView
from .websocket import CallsWSView


def setup_router(app: Application):
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE']
            )
        })

    cors.add(app.router.add_view('/api/v1/calls/', CallsView, name='calls'), webview=True)
    cors.add(app.router.add_view('/api/v1/calls/ws/', CallsWSView, name='ws'), webview=True)
    cors.add(app.router.add_view('/api/v1/record/', CallRecordsView, name='record'), webview=True)
    cors.add(app.router.add_view('/api/v1/users/', UsersView, name='users'), webview=True)
    cors.add(app.router.add_view('/api/v1/users/info/', UserInfoView, name='user_info'), webview=True)
    cors.add(app.router.add_view('/api/v1/users/register/', UsersRegisterView, name='users_register'), webview=True)
    cors.add(app.router.add_view('/api/v1/users/login/', UserLoginView, name='users_login'), webview=True)
    cors.add(app.router.add_view('/api/v1/users/login/token/', LoginByTokenView, name='login_by_token'), webview=True)
    cors.add(app.router.add_view('/api/v1/users/refresh_token/', RefreshTokenView, name='refresh_token'), webview=True)
    cors.add(app.router.add_view('/api/v1/users/revoke_token/', RevokeTokenView, name='revoke_token'), webview=True)
    cors.add(app.router.add_view('/api/v1/tags/', TagsView, name='tags'), webview=True)
    cors.add(app.router.add_view('/api/v1/permissions/', PermissionsView, name='permissions'), webview=True)
    cors.add(app.router.add_view('/api/v1/ats/info/', AtsInfoView, name='ats_info'), webview=True)


__all__ = ['CallsView', 'CallsWSView', 'CallRecordsView', 'setup_router']
