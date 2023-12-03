from flask import Flask, request
from model.base_model import db, BaseModel
from models import models
from typing import Any, Dict, Type, Tuple
from manage import create_db, drop_db, reset_db, populate_db
from peewee import DoesNotExist
from time import sleep
from itertools import count
import os


app = Flask(__name__)


@app.route("/", methods=['GET'])
def route_index():
    return {'message': "Hello, World! This is 'db_interface'."}, 200


def model_not_found_response(model_name: str) -> Tuple[Dict[str, Any], int]:
    return {"message": f"Table '{model_name}' does not exist."}, 404


def instance_not_found_response(
    model: Type[BaseModel], id: str
) -> Tuple[Dict[str, Any], int]:
    return {
        "message": f"Instance of '{model.__name__}' "
        f"with id '{id}' does not exist."
    }, 404


@app.route("/<model_name>", methods=['GET', 'POST'])
def route_model(model_name: str):
    if (model := models.get(model_name, None)) is None:
        return model_not_found_response(model_name)

    if request.method == 'GET':
        return [instance.to_dict() for instance in model.select()], 200

    elif request.method == 'POST':
        instance = model.from_dict(request.json)
        return {"id": instance.id}, 201


@app.route("/<model_name>/<id>", methods=['GET', 'PATCH', 'DELETE'])
def route_model_id(model_name: str, id: str):
    if (model := models.get(model_name, None)) is None:
        return model_not_found_response(model_name)

    try:
        instance = model.get_by_id(id)
    except DoesNotExist:
        return instance_not_found_response(model, id)

    if request.method == 'GET':
        return instance.to_dict(), 200

    elif request.method == 'PATCH':
        instance.patch(request.json)
        return {}, 200

    elif request.method == 'DELETE':
        instance.delete_instance()
        return {}, 200


@app.route("/db/create", methods=['POST'])
def route_db_create():
    create_db()
    return {}, 200


@app.route("/db/drop", methods=['POST'])
def route_db_drop():
    drop_db()
    return {}, 200


@app.route("/db/reset", methods=['POST'])
def route_db_reset():
    reset_db()
    return {}, 200


@app.route("/db/populate", methods=['POST'])
def route_db_populate():
    populate_db()
    return {}, 200


if __name__ == "__main__":
    for i in count():
        try:
            db.connect()
        except Exception as ex:
            print(ex)
            print(f"Waiting for database to be ready... ({i})", flush=True)
            sleep(1)
        else:
            print("Connected to database.", flush=True)
            break

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get('DB_INTERFACE_INTERNAL_PORT')),
        debug=True
    )
    db.close()
