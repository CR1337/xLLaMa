from model.base_model import BaseModel
from peewee import TextField
from typing import List


class StopSequence(BaseModel):
    class Meta:
        table_name = 'StopSequence'

    text = TextField(unique=True)

    @property
    def stop_sequence_usages(self) -> List[BaseModel]:
        from model import StopSequenceUsage
        return self.get_backref_list_1_n(
            StopSequenceUsage,
            StopSequenceUsage.stop_sequence,
            self
        )

    @property
    def predictions(self) -> List[BaseModel]:
        from model import Prediction, StopSequenceUsage
        return self.get_backref_list_m_n(
            Prediction,
            StopSequenceUsage,
            StopSequenceUsage.stop_sequence,
            self
        )
