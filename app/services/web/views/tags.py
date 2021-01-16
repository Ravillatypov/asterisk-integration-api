from app.api.request import RequestTag
from app.api.response import ResponseTag, ResponseTags
from app.consts import Permissions
from app.models import Tag
from app.queries import TagsQueries
from .base import BaseClientAuthView


class TagsView(BaseClientAuthView):
    async def post(self):
        """
      ---
      description: Create tag
      tags:
        - tags
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RequestTag'
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseTag'
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
        '403':
          description: Forbidden
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
      security:
        - jwt: []
        """

        self._check_permission(Permissions.tags_add)
        data = await self.get_json()
        request_model = RequestTag(**data)

        tag = await TagsQueries.create_or_update_tag(request_model)

        return ResponseTag.from_orm(tag)

    async def get(self):
        """
      ---
      description: Get tag
      tags:
        - tags
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseTags'
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
        '403':
          description: Forbidden
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseError'
      security:
        - jwt: []
        """

        self._check_permission(Permissions.tags_view)
        tags = await Tag.all()
        return ResponseTags(tags)
