from model.base_model import BaseModel
from peewee import TextField
from typing import List


class PromptPart(BaseModel):
    class Meta:
        table_name = "PromptPart"

    text = TextField()

    @property
    def prompt_part_usages(self) -> List[BaseModel]:
        from model import PromptPartUsage
        return self.get_backref_list_1_n(
            PromptPartUsage,
            PromptPartUsage.prompt_part,
            self
        )

    @property
    def predictions(self) -> List[BaseModel]:
        from model import Prediction, PromptPartUsage
        return self.get_backref_list_m_n(
            Prediction,
            PromptPartUsage,
            PromptPartUsage.prompt_part,
            self
        )
