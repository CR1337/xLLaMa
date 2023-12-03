from model.base_model import BaseModel
from peewee import IntegerField
from typing import List


class SymbolReference(BaseModel):

    start_line = IntegerField()
    end_line = IntegerField()
    start_column = IntegerField()
    end_column = IntegerField()

    @property
    def symbol_definition_references(self) -> List[BaseModel]:
        from model import SymbolDefinitionReference
        return self.get_backref_list_1_n(
            SymbolDefinitionReference,
            SymbolDefinitionReference.symbol_reference,
            self
        )

    @property
    def symbol_definitions(self) -> List[BaseModel]:
        from model import SymbolDefinition, SymbolDefinitionReference
        return self.get_backref_list_m_n(
            SymbolDefinition,
            SymbolDefinitionReference,
            SymbolDefinitionReference.symbol_reference,
            self
        )
