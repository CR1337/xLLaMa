from model.base_model import BaseModel
from model.code_snippet import CodeSnippet
from model.symbol_definition_type import SymbolDefinitionType
from peewee import TextField, IntegerField, BooleanField, ForeignKeyField
from typing import List


class SymbolDefinition(BaseModel):
    class Meta:
        table_name = "SymbolDefinition"

    symbol = TextField()
    start_line = IntegerField(null=True)
    end_line = IntegerField(null=True)
    start_column = IntegerField(null=True)
    end_column = IntegerField(null=True)
    is_builtin = BooleanField()
    code_snippet = ForeignKeyField(
        CodeSnippet, backref='_symbol_definitions'
    )
    symbol_definition_type = ForeignKeyField(
        SymbolDefinitionType, backref='_symbol_definitions'
    )

    @property
    def symbol_definition_references(self) -> List[BaseModel]:
        from model import SymbolDefinitionReference
        return self.get_backref_list_1_n(
            SymbolDefinitionReference,
            SymbolDefinitionReference.symbol_definition,
            self
        )

    @property
    def symbol_references(self) -> List[BaseModel]:
        from model import SymbolReference, SymbolDefinitionReference
        return self.get_backref_list_m_n(
            SymbolReference,
            SymbolDefinitionReference,
            SymbolDefinitionReference.symbol_definition,
            self
        )
