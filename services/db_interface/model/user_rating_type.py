from model.base_model import BaseModel
from peewee import TextField
from typing import List


class UserRatingType(BaseModel):

    name = TextField(unique=True)

    @property
    def user_ratings(self) -> List[BaseModel]:
        from model import UserRating
        return self.get_backref_list_1_n(
            UserRating,
            UserRating.user_rating_type,
            self
        )
