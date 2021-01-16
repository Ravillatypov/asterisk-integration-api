from typing import List

from app.api.request import RequestTag
from app.models import Tag


class TagsQueries:

    @staticmethod
    async def create_or_update_tag(request_model: RequestTag) -> Tag:
        tag, _ = await Tag.get_or_create(name=request_model.name.strip().title())

        if request_model.color:
            tag.color = request_model.color

        if request_model.description:
            tag.description = request_model.description

        await tag.save()

        return tag

    @staticmethod
    async def get_or_create_tags(request_models: List[RequestTag]) -> List[Tag]:
        names = [i.name for i in request_models]
        exists_names = await Tag.filter(name__in=names).values_list('name', flat=True)

        for request_model in request_models:
            if request_model.name not in exists_names:
                await TagsQueries.create_or_update_tag(request_model)

        return await Tag.filter(name__in=names)
