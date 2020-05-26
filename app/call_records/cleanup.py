import logging
from datetime import timedelta, datetime
from os import remove
from pathlib import Path

from aiomisc.service.periodic import PeriodicService

from ..models import CallRecord
from ..settings import RECORDS_STORE_DAYS


class CleanupService(PeriodicService):
    interval = 86400  # daily
    delay = 125
    __required__ = ()

    async def callback(self):
        dt = datetime.now() - timedelta(days=RECORDS_STORE_DAYS)
        async for record in CallRecord.filter(converted__isnull=False, created_at__lte=dt):
            try:
                p = Path(record.converted)
                if p.exists():
                    remove(p.as_posix())
            except Exception as err:
                logging.warning(f'Can`t remove record file: {err}')
            await record.delete()
