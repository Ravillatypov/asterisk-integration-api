from .websocket import WSReaderService, WSWriterService, CommandService

services = (WSReaderService(), WSWriterService(), CommandService(),)

__all__ = ['services']
