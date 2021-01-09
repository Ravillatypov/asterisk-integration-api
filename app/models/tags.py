from tortoise import fields

from .base import TimestampModel


class Tag(TimestampModel):
    name: str = fields.CharField(max_length=30)
    color: str = fields.CharField(max_length=20, null=True)
    description: str = fields.CharField(max_length=200, null=True)
