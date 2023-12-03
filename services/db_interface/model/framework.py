from model.base_model import BaseModel
from peewee import TextField
from typing import List


class Framework(BaseModel):
    class Meta:
        table_name = "Framework"

    name = TextField(unique=True)
    url = TextField(null=True)

    @property
    def framework_items(self) -> List[BaseModel]:
        from model import FrameworkItem
        return self.get_backref_list_1_n(
            FrameworkItem,
            FrameworkItem.framework,
            self
        )
