from model.base_model import BaseModel
from peewee import DeferredForeignKey


class SymbolDefinitionReference(BaseModel):

    symbol_definition = DeferredForeignKey(
        'SymbolDefinition', backref='_symbol_definition_references'
    )
    symbol_reference = DeferredForeignKey(
        'SymbolReference', backref='_symbol_definition_references'
    )
