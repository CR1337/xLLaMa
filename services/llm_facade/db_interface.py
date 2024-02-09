import requests
import os
from typing import Any, Dict, List


class DbInterface:

    DB_INTERFACE_PORT: int = os.environ.get('DB_INTERFACE_INTERNAL_PORT')
    DB_INTERFACE_URL: str = f"http://db_interface:{DB_INTERFACE_PORT}"

    @classmethod
    def post_llm(cls, name: str) -> Dict[str, Any]:
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/llms",
            json={"name": name}
        )
        if response.status_code == 400:
            json_response = response.json()
            if 'IntegrityError' in json_response['message']:
                return cls.get_llm_by_name(name)
        return response.json()

    @classmethod
    def delete_llm(cls, name: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{cls.DB_INTERFACE_URL}/llms/by-name/{name}"
        )
        return response.json()

    @classmethod
    def get_llms(cls) -> List[Dict[str, Any]]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/llms")
        return response.json()

    @classmethod
    def get_llm(cls, id: str) -> Dict[str, Any]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/llms/{id}")
        return response.json()

    @classmethod
    def get_llm_by_name(cls, name: str) -> Dict[str, Any]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/llms/by-name/{name}")
        return response.json()

    @classmethod
    def llm_names(cls) -> List[str]:
        return [llm['name'] for llm in cls.get_llms()]

    @classmethod
    def get_framework_item(cls, id: str) -> Dict[str, Any]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/framework_items/{id}")
        return response.json()

    @classmethod
    def get_follow_up(cls, id: str) -> Dict[str, Any]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/follow_ups/{id}")
        return response.json()

    @classmethod
    def get_prompt_part(cls, id: str) -> Dict[str, Any]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/prompt_parts/{id}")
        return response.json()

    @classmethod
    def get_system_prompt(cls, id: str) -> Dict[str, Any]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/system_prompts/{id}")
        return response.json()

    @classmethod
    def get_stop_sequence(cls, id: str) -> Dict[str, Any]:
        response = requests.get(f"{cls.DB_INTERFACE_URL}/stop_sequences/{id}")
        return response.json()

    @classmethod
    def post_prediction(
        cls,
        text: str,
        token_amount: int,
        repeat_penalty: float,
        max_tokens: int,
        seed: int,
        temperature: float,
        top_p: float,
        parent_follow_up: str,
        framework_item: str,
        llm: str,
        system_prompt: str
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/predictions",
            json={
                "text": text,
                "token_amount": token_amount,
                "repeat_penalty": repeat_penalty,
                "max_tokens": max_tokens,
                "seed": seed,
                "temperature": temperature,
                "top_p": top_p,
                "parent_follow_up": parent_follow_up,
                "framework_item": framework_item,
                "llm": llm,
                "system_prompt": system_prompt
            }
        )
        return response.json()

    @classmethod
    def post_prompt_part_usage(
        cls, position: int, prompt_part_id: str, prediction_id: str
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/prompt_part_usages",
            json={
                "position": position,
                "prompt_part": prompt_part_id,
                "prediction": prediction_id
            }
        )
        return response.json()

    @classmethod
    def post_stop_sequence_usage(
        cls, stop_sequence_id: str, prediction_id: str
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/stop_sequence_usages",
            json={
                "stop_sequence": stop_sequence_id,
                "prediction": prediction_id
            }
        )
        return response.json()
