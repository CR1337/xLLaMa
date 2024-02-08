from model.base_model import BaseModel
from model.prediction import Prediction
from peewee import (
    TextField, IntegerField, ForeignKeyField
)
from typing import List


class CodeSnippet(BaseModel):
    class Meta:
        table_name = "CodeSnippet"

    code = TextField()
    start_line = IntegerField()
    end_line = IntegerField()
    prediction = ForeignKeyField(Prediction, backref='_code_snippets')

    @property
    def undefined_symbol_references(self) -> List[BaseModel]:
        from model.undefined_symbol_reference import UndefinedSymbolReference
        return self.get_backref_list_1_n(
            UndefinedSymbolReference,
            UndefinedSymbolReference.code_snippet,
            self
        )

    @property
    def symbol_definitions(self) -> List[BaseModel]:
        from model.symbol_definition import SymbolDefinition
        return self.get_backref_list_1_n(
            SymbolDefinition,
            SymbolDefinition.code_snippet,
            self
        )
