from datetime import timedelta, datetime
from os import remove
from pathlib import Path

from aiomisc.service.periodic import PeriodicService

from app.config import app_config
from app.misc.logging import get_logger
from app.models import CallRecord

logger = get_logger('app')


class CleanupService(PeriodicService):
    interval = 86400  # daily
    delay = 125
    __required__ = ()

    async def callback(self):
        dt = datetime.now() - timedelta(days=app_config.record.store_days)
        async for record in CallRecord.filter(created_at__lte=dt).exclude(converted=None):
            try:
                p = Path(record.converted)
                if p.exists():
                    remove(p.as_posix())
            except Exception as err:
                logger.warning(f'Can`t remove record file: {err}')
            await record.delete()
