from datetime import datetime

from tortoise import fields
from tortoise.models import Model

from .consts import CallState, CallType


class TimestampModel(Model):
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


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
    records: fields.ForeignKeyNullableRelation['CallRecord']
    channels: fields.ForeignKeyRelation['Channel']


class Channel(TimestampModel):
    id: str = fields.CharField(max_length=50, pk=True)
    name: str = fields.CharField(max_length=255, index=True)
    monitor_file_name: str = fields.CharField(max_length=255, null=True)
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
