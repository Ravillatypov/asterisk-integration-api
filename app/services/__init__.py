from .asterisk import AMIService
from .cleanup import CleanupService
from .convert import ConvertService
from .find_records import FindRecordService
from .upload import UploadService
from .web import WebService
from .websocket import WSReaderService, WSWriterService, CommandService
from ..config import app_config

services = (
    WSReaderService(),
    WSWriterService(),
    CommandService(),
    WebService('0.0.0.0', 8000),
)

if app_config.record.enabled:
    services += (
        ConvertService(),
        CleanupService(),
        FindRecordService(),
        UploadService(),
    )

if app_config.ami.enabled:
    services += (AMIService(),)

__all__ = ['services']
