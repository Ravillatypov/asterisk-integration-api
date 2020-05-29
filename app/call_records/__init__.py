from .cleanup import CleanupService
from .convert import ConvertService
from .find_records import FindRecordService
from .upload import UploadService
from ..settings import RECORDS_IS_ENABLED

services = tuple()
if RECORDS_IS_ENABLED:
    services = (
        ConvertService(),
        CleanupService(),
        FindRecordService(),
        UploadService(),
    )

__all__ = ['ConvertService', 'CleanupService', 'UploadService', 'FindRecordService', 'services']
