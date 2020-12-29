from aiohttp.web_app import Application

from .calls import CallsView, CallRecordsView
from .websocket import WSView


def setup_router(app: Application):
    app.router.add_view('/api/v1/calls/', CallsView, name='calls')
    app.router.add_view('/api/v1/ws/', WSView, name='ws')
    app.router.add_view('/api/v1/record/', CallRecordsView, name='record')


__all__ = ['CallsView', 'WSView', 'CallRecordsView', 'setup_router']
