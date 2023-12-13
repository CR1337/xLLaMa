from model.base_model import BaseModel
from model.framework import Framework
from peewee import TextField, ForeignKeyField
from typing import List


class FrameworkItem(BaseModel):
    class Meta:
        table_name = "FrameworkItem"

    name = TextField(unique=True)
    url = TextField(null=True)
    description = TextField()
    source = TextField(null=True)
    framework = ForeignKeyField(Framework, backref='_framework_items')

    @property
    def predictions(self) -> List[BaseModel]:
        from model import Prediction
        return self.get_backref_list_1_n(
            Prediction,
            Prediction.framework_item,
            self
        )
