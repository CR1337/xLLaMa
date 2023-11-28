from model.base_model import db
from functools import wraps
from peewee import Model
from typing import Callable, Dict, List, Type
import sys


def db_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db.connect()
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            raise ex
        finally:
            db.close()

    return wrapper


TABLES: List[Type[Model]] = [

]


@db_session
def create_db():
    db.create_tables(TABLES)


@db_session
def drop_db():
    db.drop_tables(TABLES)


def reset_db():
    drop_db()
    create_db()


@db_session
def populate_db():
    ...  # TODO


COMMANDS: Dict[str, Callable[[None], None]] = {
    "drop": drop_db,
    "create": create_db,
    "reset": reset_db,
    "populate": populate_db,
}


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print("Usage: python manage.py [drop|create|reset|populate]")
        exit(1)
    func = COMMANDS.get(args[0], None)
    if func is None:
        print("Usage: python manage.py [drop|create|reset]")
        exit(1)
    else:
        func()


if __name__ == "__main__":
    main()
