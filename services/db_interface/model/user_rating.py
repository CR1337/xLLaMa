from model.base_model import BaseModel
from peewee import FloatField, DeferredForeignKey


class UserRating(BaseModel):
    class Meta:
        table_name = "UserRating"

    value = FloatField()
    user_rating_type = DeferredForeignKey(
        'UserRatingType', backref='_user_ratings'
    )
    prediction = DeferredForeignKey('Prediction', backref='_user_ratings')
