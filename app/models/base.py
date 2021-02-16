from datetime import datetime

from tortoise import fields
from tortoise.models import Model


class TimestampModel(Model):
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class Version(Model):
    version: int = fields.SmallIntField()
