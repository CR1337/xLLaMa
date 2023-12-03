from model.base_model import BaseModel
from peewee import DeferredForeignKey


class FollowUp(BaseModel):
    class Meta:
        table_name = "FollowUp"

    parent_prediction = DeferredForeignKey(
        'Prediction', backref="_follow_up_children"
    )
    follow_up_type = DeferredForeignKey(
        'FollowUpType', backref="_follow_ups"
    )

    @property
    def child_prediction(self) -> BaseModel:
        from model import Prediction
        return Prediction.get(Prediction.parent_follow_up == self)
