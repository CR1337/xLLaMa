from model.base_model import BaseModel
from model.code_snippet import CodeSnippet
from peewee import TextField, IntegerField, ForeignKeyField


class SymbolReference(BaseModel):
    class Meta:
        table_name = "SymbolReference"

    symbol = TextField()
    start_line = IntegerField()
    end_line = IntegerField()
    start_column = IntegerField()
    end_column = IntegerField()
    code_snippet = ForeignKeyField(
        CodeSnippet, backref='_symbol_references'
    )
