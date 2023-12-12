from __future__ import annotations
from model.base_model import BaseModel
from peewee import TextField, FloatField, IntegerField, DeferredForeignKey
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
        'FollowUp', backref='_follow_up_prediction'
    )
    framework_item = DeferredForeignKey(
        'FrameworkItem', backref='_predictions'
    )
    llm = DeferredForeignKey('Llm', backref='_predictions')
    system_prompt = DeferredForeignKey(
        'SystemPrompt', backref='_predictions'
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
