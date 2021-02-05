from app.api.response import ResponseAtsInfo
from .base import BaseView


class AtsInfoView(BaseView):

    async def get(self):
        """
      ---
      description: Get ats info
      tags:
        - system
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResponseAtsInfo'
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
        """

        return ResponseAtsInfo(
            company_name=self.conf.ats.company_name,
            company_logo=self.conf.ats.company_logo,
            group_numbers=self.conf.ats.group_numbers,
            external_numbers=self.conf.ats.trunks,
        )
