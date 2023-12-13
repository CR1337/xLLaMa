from model.base_model import BaseModel
from model.symbol_definition import SymbolDefinition
from model.symbol_reference import SymbolReference
from peewee import ForeignKeyField


class SymbolDefinitionReference(BaseModel):
    class Meta:
        table_name = "SymbolDefinitionReference"

    symbol_definition = ForeignKeyField(
        SymbolDefinition, backref='_symbol_definition_references'
    )
    symbol_reference = ForeignKeyField(
        SymbolReference, backref='_symbol_definition_references'
    )
