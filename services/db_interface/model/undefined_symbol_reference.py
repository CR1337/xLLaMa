from model.base_model import BaseModel
from peewee import TextField, IntegerField, DeferredForeignKey


class UndefinedSymbolReference(BaseModel):
    class Meta:
        table_name = "UndefinedSymbolReference"

    symbol = TextField()
    start_line = IntegerField()
    end_line = IntegerField()
    start_column = IntegerField()
    end_column = IntegerField()
    code_snippet = DeferredForeignKey(
        'CodeSnippet', backref='_undefined_symbol_references'
    )
