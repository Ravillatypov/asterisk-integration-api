from .cleanup import CleanupService
from .convert import ConvertService
from .find_records import FindRecordService
from .upload import UploadService

services = (
    ConvertService(),
    CleanupService(),
    FindRecordService(),
    UploadService(),
)
__all__ = ['ConvertService', 'CleanupService', 'UploadService', 'FindRecordService', 'services']
