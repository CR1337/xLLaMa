from model.base_model import BaseModel
from peewee import TextField, DeferredForeignKey
from typing import List


class FrameworkItem(BaseModel):
    class Meta:
        table_name = "FrameworkItem"

    name = TextField(unique=True)
    url = TextField(null=True)
    description = TextField()
    source = TextField()
    framework = DeferredForeignKey('Framework', backref='_framework_items')

    @property
    def preditions(self) -> List[BaseModel]:
        from model import Prediction
        return self.get_backref_list_1_n(
            Prediction,
            Prediction.framework_item,
            self
        )
