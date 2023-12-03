from model.base_model import BaseModel
from peewee import TextField
from typing import List


class Llm(BaseModel):
    class Meta:
        table_name = 'Llm'

    name = TextField(unique=True)

    @property
    def predictions(self) -> List[BaseModel]:
        from model import Prediction
        return self.get_backref_list_1_n(
            Prediction,
            Prediction.llm,
            self
        )
