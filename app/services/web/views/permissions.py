from app.api.response import ResponsePermissions, ResponsePermission
from app.consts import Permissions
from .base import BaseClientAuthView


class PermissionsView(BaseClientAuthView):
    async def get(self):
        result = [ResponsePermission.from_orm(i) for i in Permissions.all()]
        return ResponsePermissions(result=result)
