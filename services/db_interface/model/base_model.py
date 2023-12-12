from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from typing import Any, Dict, Generator, Tuple, Iterable, List, Type
from peewee import (
    DateTimeField,
    Model,
    PostgresqlDatabase,
    TextField,
    Field,
    DeferredForeignKey
)
import os

db: PostgresqlDatabase

if os.environ.get('TEST') == "1":
    db = PostgresqlDatabase(
        database=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('TEST_POSTGRES_HOST'),
        port=os.environ.get('TEST_DB_INTERNAL_PORT')
    )
else:
    db = PostgresqlDatabase(
        database=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST'),
        port=os.environ.get('DB_INTERNAL_PORT')
    )


class BaseModel(Model):
    class Meta:
        database = db
        table_name = "BaseModel"

    id = TextField(primary_key="True", default=uuid4)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def _serialize_value(self, key: str) -> Any:
        cls_attr = getattr(self.__class__, key)
        value = getattr(self, key)
        if isinstance(cls_attr, DeferredForeignKey):
            return value.id
        elif isinstance(value, Iterable):
            return [self._serialize_value(v) for v in value]
        else:
            return value

    def to_dict(self) -> Dict[str, Any]:
        cls = self.__class__
        return {
            key: (
                getattr(self, key).id
                if isinstance(getattr(cls, key), DeferredForeignKey)
                else getattr(self, key)
            )
            for key in dir(cls)
            if (
                isinstance(getattr(cls, key), (property, Field))
                and key not in ('_pk', 'dirty_fields')
            )
        }

    @classmethod
    def _filter_dict(
        cls, kwargs: Dict[str, Any]
    ) -> Generator[Tuple[str, Any], None, None]:
        return (
            (key, value)
            for (key, value) in kwargs.items()
            if key not in (
                'id', 'created_at', 'updated_at', '_pk', 'dirty_fields'
            )
            and isinstance(getattr(cls, key, None), Field)
        )

    def patch(self, kwargs: Dict[str, Any]):
        for key, value in self._filter_dict(kwargs):
            setattr(self, key, value)
        self.save()

    @classmethod
    def from_dict(cls, kwargs: Dict[str, Any]) -> BaseModel:
        return cls.create(**dict(cls._filter_dict(kwargs)))

    @classmethod
    def get_backref_list_1_n(
        cls,
        backref_model: Type[BaseModel],
        backref_field: Field,
        instance: BaseModel
    ) -> List[BaseModel]:
        return [
            x for x in backref_model.select().where(
                backref_field == instance
            )
        ]

    @classmethod
    def get_backref_list_m_n(
        cls,
        backref_model: Type[BaseModel],
        relation_model: Type[BaseModel],
        relation_field: Field,
        instance: BaseModel
    ) -> List[BaseModel]:
        return [
            x for x in backref_model.select().join(
                relation_model
            ).where(
                relation_field == instance
            )
        ]
