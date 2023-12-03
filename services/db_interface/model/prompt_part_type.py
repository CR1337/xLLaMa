from model.base_model import BaseModel
from peewee import TextField
from typing import List


class PromptPartType(BaseModel):

    name = TextField(unique=True)

    @property
    def prompt_parts(self) -> List[BaseModel]:
        from model import PromptPart
        return self.get_backref_list_1_n(
            PromptPart,
            PromptPart.prompt_part_type,
            self
        )
