from model.base_model import BaseModel
from peewee import IntegerField, DeferredForeignKey


class PromptPartUsage(BaseModel):
    class Meta:
        table_name = "PromptPartUsage"

    position = IntegerField()
    prompt_part = DeferredForeignKey(
        'PromptPart', backref='_prompt_part_usages'
    )
    prediction = DeferredForeignKey(
        'Prediction', backref='_prompt_part_usages'
    )
