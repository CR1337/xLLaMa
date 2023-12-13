import pytest
from ..util.db_interaction import (
    reset_database, populate_database, get_instances, get_instance_by_name,
    post_instance, get_instance
)
import json
from typing import Dict, Any


class TestDatabaseInterfaceGet:

    DUMMY_DATA_FILENAME: str = "tests/db_interface/test_02_get_db_dummy_data.json"
    with open(DUMMY_DATA_FILENAME, "r") as file:
        DUMMY_DATA = json.load(file)

    @pytest.fixture()
    def instance_ids(self, method_wrapper: None) -> Dict[str, Any]:
        instance_ids = {}
        for model_name, data in self.DUMMY_DATA.items():
            processed_data = {}

            for key, value in data.items():
                if value is None:
                    processed_data[key] = None
                elif not isinstance(value, str):
                    processed_data[key] = value
                elif value.startswith("$"):
                    processed_data[key] = instance_ids[value[1:]]
                elif value.startswith("§"):
                    data_model_name, type_name = value[1:].split(":")
                    processed_data[key] = get_instance_by_name(
                        data_model_name, type_name
                    )[0]["id"]
                else:
                    processed_data[key] = value

            model_name_for_post = (
                model_name[1:] if model_name.startswith("@") else model_name
            )

            instance_ids[model_name] = post_instance(
                model_name_for_post, processed_data
            )[0]["id"]
        return instance_ids

    @pytest.fixture(autouse=True)
    def method_wrapper(self):
        reset_database()
        populate_database()
        yield
        reset_database()
        populate_database()

    @pytest.mark.parametrize("model_name, instance_name", [
        ("follow_up_types", "too_short"),
        ("symbol_definition_types", "import"),
        ("user_rating_types", "sentiment"),
        ("llms", "llm_1")
    ])
    def test_get_instance_by_name(
        self, model_name: str, instance_name: str, instance_ids: Dict[str, Any]
    ):
        response, status_code = get_instance_by_name(model_name, instance_name)
        assert status_code == 200
        assert isinstance(response, dict)
        assert "id" in response
        assert isinstance(response["id"], str)
        assert "created_at" in response
        assert isinstance(response["created_at"], str)
        assert "updated_at" in response
        assert isinstance(response["updated_at"], str)

    @pytest.mark.parametrize("model_name", [
        "predictions",
        "follow_ups",
        "follow_up_types",
        "framework_items",
        "llms",
        "prompt_parts",
        "system_prompts",
        "stop_sequences",
        "code_snippets",
        "user_ratings",
        "frameworks",
        "prompt_part_usages",
        "stop_sequence_usages",
        "symbol_definitions",
        "symbol_definition_types",
        "symbol_references",
        "symbol_definition_references",
        "undefined_symbol_references",
        "user_rating_types"
    ])
    def test_get_instances(self, model_name: str):
        response, status_code = get_instances(model_name)
        assert status_code == 200
        assert isinstance(response, list)
        for instance in response:
            assert isinstance(instance, dict)
            assert "id" in instance
            assert isinstance(instance["id"], str)
            assert "created_at" in instance
            assert isinstance(instance["created_at"], str)
            assert "updated_at" in instance
            assert isinstance(instance["updated_at"], str)

    @pytest.mark.parametrize("model_name", [
        "predictions",
        "follow_ups",
        "follow_up_types",
        "framework_items",
        "llms",
        "prompt_parts",
        "system_prompts",
        "stop_sequences",
        "code_snippets",
        "user_ratings",
        "frameworks",
        "prompt_part_usages",
        "stop_sequence_usages",
        "symbol_definitions",
        "symbol_definition_types",
        "symbol_references",
        "symbol_definition_references",
        "undefined_symbol_references",
        "user_rating_types"
    ])
    def test_get_instance(self, model_name: str, instance_ids: Dict[str, Any]):
        response, status_code = get_instance(
            model_name, instance_ids[model_name]
        )
        assert status_code == 200
        assert isinstance(response, dict)
        assert "id" in response
        assert response["id"] == instance_ids[model_name]
        assert isinstance(response["id"], str)
        assert "created_at" in response
        assert isinstance(response["created_at"], str)
        assert "updated_at" in response
        assert isinstance(response["updated_at"], str)
        for key, value in self.DUMMY_DATA[model_name].items():
            if key.startswith("@"):
                continue
            if value is None:
                assert response[key] is None
            elif not isinstance(value, str):
                assert response[key] == value
            elif value.startswith("$"):
                assert response[key] == instance_ids[value[1:]]
            elif value.startswith("§"):
                data_model_name, type_name = value[1:].split(":")
                assert response[key] == get_instance_by_name(
                    data_model_name, type_name
                )[0]["id"]
            else:
                assert response[key] == value
