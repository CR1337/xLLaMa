from model.base_model import BaseModel
from peewee import TextField
from typing import List


class SystemPrompt(BaseModel):
    class Meta:
        table_name = "SystemPrompt"

    text = TextField()
    name = TextField()

    @property
    def predictions(self) -> List[BaseModel]:
        from model import Prediction
        return self.get_backref_list_1_n(
            Prediction,
            Prediction.system_prompt,
            self
        )
