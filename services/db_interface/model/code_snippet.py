from model.base_model import BaseModel
from model.prediction import Prediction
from peewee import (
    TextField, IntegerField, FloatField, FixedCharField, ForeignKeyField
)
from typing import Tuple, List


class CodeSnippet(BaseModel):
    class Meta:
        table_name = "CodeSnippet"

    CYCLOMATIC_COMPLEXITY_RANK_CHOICES: Tuple[str, ...] = (
        "A", "B", "C", "D", "E", "F"
    )
    MAINTAINABILITY_INDEX_RANK_CHOICES: Tuple[str, ...] = ("A", "B", "C")

    code = TextField()
    start_line = IntegerField()
    end_line = IntegerField()
    raw_loc = IntegerField()
    raw_lloc = IntegerField()
    raw_sloc = IntegerField()
    raw_comments = IntegerField()
    raw_multi = IntegerField()
    raw_single_comments = IntegerField()
    raw_blank = IntegerField()
    halstead_h1 = IntegerField()
    halstead_h2 = IntegerField()
    halstead_N1 = IntegerField()
    halstead_N2 = IntegerField()
    halstead_length = FloatField()
    halstead_volume = FloatField()
    halstead_difficulty = FloatField()
    halstead_effort = FloatField()
    halstead_time = FloatField()
    halstead_bugs = FloatField()
    cyclomatic_complexity_score = FloatField()
    cyclomatic_complexity_rank = FixedCharField(
        max_length=1, choices=CYCLOMATIC_COMPLEXITY_RANK_CHOICES
    )
    maintainability_index_score = FloatField()
    maintainability_index_rank = FixedCharField(
        max_length=1, choices=MAINTAINABILITY_INDEX_RANK_CHOICES
    )
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
