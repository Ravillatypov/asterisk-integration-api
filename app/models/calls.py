from datetime import datetime

from tortoise import fields

from .base import TimestampModel
from .tags import Tag
from ..consts import CallState, CallType, IntegrationState
from ..utils import add_city_code, convert_datetime


class Call(TimestampModel):
    id: str = fields.CharField(max_length=50, pk=True)
    from_pin: str = fields.CharField(max_length=6, default='')
    from_number: str = fields.CharField(max_length=20, default='')
    request_number: str = fields.CharField(max_length=20, default='')
    request_pin: str = fields.CharField(max_length=6, default='')
    voice_started_at: datetime = fields.DatetimeField(null=True)
    finished_at: datetime = fields.DatetimeField(null=True)
    call_type: CallType = fields.CharEnumField(CallType, default=CallType.UNKNOWN)
    state: CallState = fields.CharEnumField(CallState, default=CallState.NEW)
    integration_state: IntegrationState = fields.CharEnumField(IntegrationState, null=True)
    account_id: str = fields.CharField(max_length=50, null=True)
    record: fields.ForeignKeyNullableRelation['CallRecord'] = fields.ForeignKeyField('models.Call', null=True)
    external_id: str = fields.CharField(max_length=70, index=True, null=True)
    comment: str = fields.CharField(max_length=512, default='')
    user: str = fields.CharField(max_length=128, default='')
    record_path: str = fields.CharField(max_length=255, null=True)
    tags: fields.ManyToManyRelation[Tag] = fields.ManyToManyField(
        'models.Tag', related_name='calls', through='call_tags'
    )

    records: fields.ForeignKeyNullableRelation['CallRecord']
    channels: fields.ForeignKeyRelation['Channel']

    def event_schema(self) -> dict:
        waiting_time = duration = None

        if self.voice_started_at:
            waiting_time = (self.voice_started_at - self.created_at).seconds

        if self.finished_at and self.voice_started_at:
            duration = (self.finished_at - self.voice_started_at).seconds

        return {
            'id': self.id,
            'started_at': convert_datetime(self.created_at),
            'voice_started_at': convert_datetime(self.voice_started_at),
            'finished_at': convert_datetime(self.finished_at),
            'call_type': self.call_type.value,
            'state': self.state.value,
            'is_record': bool(self.record_id),
            'from_pin': self.from_pin,
            'from_number': add_city_code(self.from_number),
            'request_number': add_city_code(self.request_number),
            'request_pin': self.request_pin,
            'account_id': self.account_id,
            'waiting_time': waiting_time,
            'duration': duration,
            'comment': self.comment,
        }

    @property
    def is_finished(self) -> bool:
        return self.state in (CallState.END, CallState.NOT_CONNECTED, CallState.MISSED)

    @property
    def is_record(self) -> bool:
        return self.state == CallState.END and self.record_path is not None

    @property
    def started_at(self) -> datetime:
        return self.created_at


class Channel(TimestampModel):
    id: str = fields.CharField(max_length=50, pk=True)
    name: str = fields.CharField(max_length=255, index=True)
    monitor_file_name: str = fields.CharField(max_length=255, null=True)
    pin: str = fields.CharField(max_length=6, default='')
    from_number: str = fields.CharField(max_length=20, default='')
    request_number: str = fields.CharField(max_length=20, default='')
    bridged: fields.ManyToManyRelation['Channel'] = fields.ManyToManyField('models.Channel', related_name='bridged_set')
    call: fields.ForeignKeyNullableRelation['Call'] = fields.ForeignKeyField('models.Call', related_name='channels',
                                                                             null=True)
    bridged_set: fields.ManyToManyRelation['Channel']
    records: fields.ForeignKeyNullableRelation['CallRecord']


class CallRecord(TimestampModel):
    call: fields.ForeignKeyNullableRelation['Call'] = fields.ForeignKeyField('models.Call', related_name='records',
                                                                             null=True)
    channel: fields.ForeignKeyRelation['Channel'] = fields.ForeignKeyField('models.Channel', related_name='records')
    converted: str = fields.CharField(max_length=255, null=True)
    file_name: str = fields.CharField(max_length=255)
    duration: int = fields.IntField(null=True)
