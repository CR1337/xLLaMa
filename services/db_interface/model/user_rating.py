from model.base_model import BaseModel
from model.user_rating_type import UserRatingType
from model.prediction import Prediction
from peewee import FloatField, ForeignKeyField


class UserRating(BaseModel):
    class Meta:
        table_name = "UserRating"

    value = FloatField()
    user_rating_type = ForeignKeyField(
        UserRatingType, backref='_user_ratings'
    )
    prediction = ForeignKeyField(Prediction, backref='_user_ratings')
