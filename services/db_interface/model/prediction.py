from model.base_model import BaseModel
from model.framework_item import FrameworkItem
from model.llm import Llm
from model.system_prompt import SystemPrompt
from peewee import (
    TextField, FloatField, IntegerField, ForeignKeyField, DeferredForeignKey
)
from typing import List


class Prediction(BaseModel):
    class Meta:
        table_name = 'Prediction'

    text = TextField()
    token_amount = IntegerField()
    repeat_penalty = FloatField()
    max_tokens = IntegerField()
    seed = IntegerField()
    temperature = FloatField()
    top_p = FloatField()
    parent_follow_up = DeferredForeignKey(
        'FollowUp', backref='_follow_up_prediction', null=True
    )
    framework_item = ForeignKeyField(
        FrameworkItem, backref='_predictions'
    )
    llm = ForeignKeyField(Llm, backref='_predictions')
    system_prompt = ForeignKeyField(
        SystemPrompt, backref='_predictions', null=True
    )

    @property
    def follow_up_children(self) -> List[BaseModel]:
        from model import FollowUp
        return self.get_backref_list_1_n(
            FollowUp,
            FollowUp.parent_prediction,
            self
        )

    @property
    def prompt_part_usages(self) -> List[BaseModel]:
        from model import PromptPartUsage
        return self.get_backref_list_1_n(
            PromptPartUsage,
            PromptPartUsage.prediction,
            self
        )

    @property
    def prompt_parts(self) -> List[BaseModel]:
        from model import PromptPart, PromptPartUsage
        return self.get_backref_list_m_n(
            PromptPart,
            PromptPartUsage,
            PromptPartUsage.prediction,
            self
        )

    @property
    def stop_sequence_usages(self) -> List[BaseModel]:
        from model import StopSequenceUsage
        return self.get_backref_list_1_n(
            StopSequenceUsage,
            StopSequenceUsage.prediction,
            self
        )

    @property
    def stop_sequences(self) -> List[BaseModel]:
        from model import StopSequence, StopSequenceUsage
        return self.get_backref_list_m_n(
            StopSequence,
            StopSequenceUsage,
            StopSequenceUsage.prediction,
            self
        )

    @property
    def user_ratings(self) -> List[BaseModel]:
        from model import UserRating
        return self.get_backref_list_1_n(
            UserRating,
            UserRating.prediction,
            self
        )

    @property
    def code_snippets(self) -> List[BaseModel]:
        from model import CodeSnippet
        return self.get_backref_list_1_n(
            CodeSnippet,
            CodeSnippet.prediction,
            self
        )
