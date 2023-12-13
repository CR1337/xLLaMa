from model.base_model import BaseModel
from model.prediction import Prediction
from model.follow_up_type import FollowUpType
from peewee import ForeignKeyField


class FollowUp(BaseModel):
    class Meta:
        table_name = "FollowUp"

    parent_prediction = ForeignKeyField(
        Prediction, backref="_follow_up_children"
    )
    follow_up_type = ForeignKeyField(
        FollowUpType, backref="_follow_ups"
    )

    @property
    def child_prediction(self) -> BaseModel:
        from model import Prediction
        return Prediction.get(Prediction.parent_follow_up == self)
