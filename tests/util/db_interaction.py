import requests
from tests.util.environment import environment
from typing import Any, Dict, Tuple
import json


DB_INTERFACE_HOST = '127.0.0.1'
DB_INTERFACE_PORT = environment['DB_INTERFACE_EXTERNAL_PORT']
DB_INTERFACE_URL = f'http://{DB_INTERFACE_HOST}:{DB_INTERFACE_PORT}'

DUMMY_DATA_FILENAME: str = "tests/util/dummy_data.json"
with open(DUMMY_DATA_FILENAME, "r") as file:
    DUMMY_DATA = json.load(file)


def get_index() -> Tuple[Dict[str, Any], int]:
    response = requests.get(f'{DB_INTERFACE_URL}/')
    return response.json(), response.status_code


def create_database() -> Tuple[Dict[str, Any], int]:
    response = requests.post(f'{DB_INTERFACE_URL}/db/create')
    return response.json(), response.status_code


def drop_database() -> Tuple[Dict[str, Any], int]:
    response = requests.post(f'{DB_INTERFACE_URL}/db/drop')
    return response.json(), response.status_code


def reset_database() -> Tuple[Dict[str, Any], int]:
    response = requests.post(f'{DB_INTERFACE_URL}/db/reset')
    return response.json(), response.status_code


def populate_database() -> Tuple[Dict[str, Any], int]:
    response = requests.post(f'{DB_INTERFACE_URL}/db/populate')
    return response.json(), response.status_code


def get_instance_by_name(
    model_name: str, name: str
) -> Tuple[Dict[str, Any], int]:
    response = requests.get(f'{DB_INTERFACE_URL}/{model_name}/by-name/{name}')
    return response.json(), response.status_code


def get_instances(model_name: str) -> Tuple[Dict[str, Any], int]:
    response = requests.get(f'{DB_INTERFACE_URL}/{model_name}')
    return response.json(), response.status_code


def post_instance(
    model_name: str, data: Dict[str, Any]
) -> Tuple[Dict[str, Any], int]:
    response = requests.post(f'{DB_INTERFACE_URL}/{model_name}', json=data)
    return response.json(), response.status_code


def get_instance(model_name: str, id: str) -> Tuple[Dict[str, Any], int]:
    response = requests.get(f'{DB_INTERFACE_URL}/{model_name}/{id}')
    return response.json(), response.status_code


def patch_instance(
    model_name: str, id: str, data: Dict[str, Any]
) -> Tuple[Dict[str, Any], int]:
    response = requests.patch(
        f'{DB_INTERFACE_URL}/{model_name}/{id}', json=data
    )
    return response.json(), response.status_code


def delete_instance(model_name: str, id: str) -> Tuple[Dict[str, Any], int]:
    response = requests.delete(f'{DB_INTERFACE_URL}/{model_name}/{id}')
    return response.json(), response.status_code


def post_dummy_data() -> Dict[str, Any]:
    instance_ids = {}
    for model_name, data in DUMMY_DATA.items():
        processed_data = {}
        for key, value in data.items():
            if value is None:
                processed_data[key] = None
            elif not isinstance(value, str):
                processed_data[key] = value
            elif value.startswith("$"):
                processed_data[key] = instance_ids[value[1:]]
            else:
                processed_data[key] = value
        model_name_for_post = (
            model_name[1:] if model_name.startswith("@") else model_name
        )
        instance_ids[model_name] = post_instance(
            model_name_for_post, processed_data
        )[0]["id"]
    return instance_ids
