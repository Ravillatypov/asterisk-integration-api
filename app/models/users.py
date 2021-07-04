from datetime import datetime
from hashlib import sha3_256
from typing import List

from tortoise import fields, models

from .base import TimestampModel
from ..consts import Permissions


class User(TimestampModel):
    is_active: bool = fields.BooleanField(default=True)
    username: str = fields.CharField(max_length=30, unique=True)
    first_name: str = fields.CharField(max_length=30, default='')
    last_name: str = fields.CharField(max_length=30, default='')
    pass_hash: str = fields.CharField(max_length=255, default='')
    company_id: int = fields.SmallIntField(null=True)
    permissions: List[int] = fields.JSONField(default=[Permissions.calls_view.value,
                                                       Permissions.tags_view.value,
                                                       Permissions.users_view.value])

    def set_password(self, new_pass: str):
        self.pass_hash = self.get_pass_hash(new_pass)

    def is_valid_password(self, password: str) -> bool:
        return self.pass_hash == self.get_pass_hash(password)

    @classmethod
    def get_pass_hash(cls, password: str) -> str:
        return sha3_256(password.encode()).hexdigest()


class Token(models.Model):
    refresh_token: str = fields.CharField(max_length=512)
    expired_at: datetime = fields.DatetimeField()
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', on_delete=fields.CASCADE, null=True)
