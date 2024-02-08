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
    def symbol_references(self) -> List[BaseModel]:
        from model.symbol_reference import SymbolReference
        return self.get_backref_list_1_n(
            SymbolReference,
            SymbolReference.code_snippet,
            self
        )
