import requests
from tests.util.environment import environment
from typing import Any, Dict, Tuple, List


LLM_FACADE_HOST = '127.0.0.1'
LLM_FACADE_PORT = environment['LLM_FACADE_EXTERNAL_PORT']
LLM_FACADE_URL = f'http://{LLM_FACADE_HOST}:{LLM_FACADE_PORT}'


def get_models() -> Tuple[Dict[str, Any], int]:
    response = requests.get(f'{LLM_FACADE_URL}/models')
    return response.json(), response.status_code


def install_model(model_name: str) -> Tuple[Dict[str, Any], int]:
    response = requests.get(
        f'{LLM_FACADE_URL}/models/install?model={model_name}&stream=false'
    )
    return response.json(), response.status_code


def generate(
    model_id: str,
    framework_item_id: str,
    prompt_part_ids: List[str],
    kwargs: Dict[str, Any]
) -> Tuple[Dict[str, Any], int]:
    response = requests.get(
        f'{LLM_FACADE_URL}/generate'
        f'?model={model_id}'
        f'&framework_item={framework_item_id}'
        f'&prompt_parts={",".join(prompt_part_ids)}'
        f'&stream=false'
        f'&{"&".join([f"{key}={value}" for key, value in kwargs.items()])}'
    )
    return response.json(), response.status_code
