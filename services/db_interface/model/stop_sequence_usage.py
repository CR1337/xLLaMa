from model.base_model import BaseModel
from model.stop_sequence import StopSequence
from model.prediction import Prediction
from peewee import ForeignKeyField


class StopSequenceUsage(BaseModel):
    class Meta:
        table_name = "StopSequenceUsage"

    stop_sequence = ForeignKeyField(
        StopSequence, backref='_stop_sequence_usages'
    )
    prediction = ForeignKeyField(
        Prediction, backref='_stop_sequence_usages'
    )
