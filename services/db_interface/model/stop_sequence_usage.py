from model.base_model import BaseModel
from peewee import DeferredForeignKey


class StopSequenceUsage(BaseModel):
    class Meta:
        table_name = "StopSequenceUsage"

    stop_sequence = DeferredForeignKey(
        'StopSequence', backref='_stop_sequence_usages'
    )
    prediction = DeferredForeignKey(
        'Prediction', backref='_stop_sequence_usages'
    )
