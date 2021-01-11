from app.api.request import RequestTag
from app.api.response import ResponseTag, ResponseTags
from app.consts import Permissions
from app.models import Tag
from .base import BaseClientAuthView


class TagsView(BaseClientAuthView):
    async def post(self):
        self._check_permission(Permissions.tags_add)
        data = await self.get_json()
        request_model = RequestTag(**data)

        tag, _ = await Tag.get_or_create(name=request_model.name.strip().title())
        if request_model.color:
            tag.color = request_model.color

        if request_model.description:
            tag.description = request_model.description

        await tag.save()

        return ResponseTag.from_orm(tag)

    async def get(self):
        self._check_permission(Permissions.tags_view)
        tags = await Tag.all()
        return ResponseTags(tags)
