from os.path import getsize
from typing import List, Optional

from aiomisc.service.periodic import PeriodicService
from tortoise.functions import Count

from app.consts import CallState
from app.models import CallRecord, Call
from app.utils import get_mp3_file_duration, convert_record, get_full_path


class ConvertService(PeriodicService):
    interval = 10  # seconds
    delay = 5
    __required__ = ()

    async def callback(self):
        query = Call.all().order_by('-created_at').annotate(
            records_count=Count('records')
        ).prefetch_related('records').filter(
            state=CallState.END,
            record_path=None,
            records_count__gte=1
        ).limit(50)

        async for call in query:
            record = self._choice_record(call.records)

            record.converted = await convert_record(record.full_path, call.id)
            record.duration = await get_mp3_file_duration(record.converted)

            if record.converted:
                await record.save()

            call.record_path = record.converted
            await call.save()

    @staticmethod
    def _choice_record(records: List[CallRecord]) -> Optional[CallRecord]:
        record_sizes = {}

        for record in records:
            record.full_path = get_full_path(record.file_name)

            if record.full_path:
                record_sizes[getsize(record.full_path)] = record

        return record_sizes.get(max(record_sizes))
