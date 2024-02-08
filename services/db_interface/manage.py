from model import (
    db, BaseModel, UserRatingType, Framework, FrameworkItem,
    FollowUpType, Prediction, SystemPrompt,
    StopSequence
)
from models import models
from functools import wraps
from typing import Callable, Dict, List, Type
import sys
from peewee import DeferredForeignKey
import json


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


TABLES: List[Type[BaseModel]] = [
    model for model in models.values()
] + [BaseModel]


@db_session
def create_db():
    DeferredForeignKey.resolve(Prediction)
    db.create_tables(TABLES)


@db_session
def drop_db():
    db.execute_sql('SET session_replication_role = REPLICA;')
    db.drop_tables(TABLES, safe=True)
    db.execute_sql('SET session_replication_role = DEFAULT;')


def reset_db():
    drop_db()
    create_db()


@db_session
def populate_db():
    with open("init_data/system_prompts.json", 'r') as file:
        system_prompts_data = json.load(file)
    for system_prompt in system_prompts_data:
        SystemPrompt.from_dict(system_prompt)

    with open("init_data/follow_up_types.json", 'r') as file:
        follow_up_types_data = json.load(file)
    for follow_up_type in follow_up_types_data:
        FollowUpType.from_dict(follow_up_type)

    with open("init_data/user_rating_types.json", 'r') as file:
        user_rating_types_data = json.load(file)
    for user_rating_type in user_rating_types_data:
        UserRatingType.from_dict(user_rating_type)

    with open("init_data/frameworks.json", 'r') as file:
        frameworks_data = json.load(file)
    with open("init_data/framework_items.json", 'r') as file:
        framework_items_data = json.load(file)
    for framework, framework_items in zip(
        frameworks_data, framework_items_data
    ):
        framework = Framework.from_dict(framework)
        for framework_item in framework_items:
            framework_item["framework_id"] = framework.id
            FrameworkItem.from_dict(framework_item)

    with open("init_data/stop_sequences.json", 'r') as file:
        stop_sequences_data = json.load(file)
    for stop_sequence in stop_sequences_data:
        stop_sequence = StopSequence.from_dict(stop_sequence)


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
        print("Usage: python manage.py [drop|create|reset|populate]")
        exit(1)
    else:
        func()


if __name__ == "__main__":
    main()
