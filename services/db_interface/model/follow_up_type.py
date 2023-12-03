from model.base_model import BaseModel
from peewee import TextField
from typing import List


class FollowUpType(BaseModel):
    class Meta:
        table_name = "FollowUpType"

    name = TextField(unique=True)

    @property
    def follow_ups(self) -> List[BaseModel]:
        from model import FollowUp
        return self.get_backref_list_1_n(
            FollowUp,
            FollowUp.follow_up_type,
            self
        )
