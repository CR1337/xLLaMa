from model.base_model import BaseModel
from peewee import TextField
from typing import List


class SymbolDefinitionType(BaseModel):

    name = TextField(unique=True)

    @property
    def symbol_definitions(self) -> List[BaseModel]:
        from model import SymbolDefinition
        return self.get_backref_list_1_n(
            SymbolDefinition,
            SymbolDefinition.symbol_definition_type,
            self
        )
