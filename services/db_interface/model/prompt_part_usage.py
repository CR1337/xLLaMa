from model.base_model import BaseModel
from model.prompt_part import PromptPart
from model.prediction import Prediction
from peewee import IntegerField, ForeignKeyField


class PromptPartUsage(BaseModel):
    class Meta:
        table_name = "PromptPartUsage"

    position = IntegerField()
    prompt_part = ForeignKeyField(
        PromptPart, backref='_prompt_part_usages'
    )
    prediction = ForeignKeyField(
        Prediction, backref='_prompt_part_usages'
    )
