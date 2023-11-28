from datetime import datetime
from uuid import uuid4
from abc import abstractmethod
from typing import Any, Dict

from peewee import DateTimeField, Model, PostgresqlDatabase, TextField

DATABASE_URL: str = "postgres://postgres:postgres@localhost:5432/postgres"
db: PostgresqlDatabase = PostgresqlDatabase(DATABASE_URL)


class BaseModel(Model):
    class Meta:
        database = db

    id = TextField(primary_key="True", default=uuid4)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError("This is an abstract method.")
