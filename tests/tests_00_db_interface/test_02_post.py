import pytest
from ..util.db_interaction import (
    reset_database, populate_database, post_dummy_data, post_instance,
    DUMMY_DATA
)
from typing import Dict, Any


class TestDatabaseInterfacePost:

    @pytest.fixture()
    def instance_ids(self, method_wrapper: None) -> Dict[str, Any]:
        return post_dummy_data()

    @pytest.fixture(autouse=True)
    def method_wrapper(self):
        reset_database()
        populate_database()
        yield
        reset_database()
        populate_database()

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
        "symbol_references",
        "user_rating_types"
    ])
    def test_post_instance(
        self, model_name: str, instance_ids: Dict[str, Any]
    ):
        dummy_data = DUMMY_DATA[model_name]
        post_data = {}
        for key, value in dummy_data.items():
            if value is None:
                post_data[key] = None
            elif isinstance(value, (int, float)):
                post_data[key] = value + 1
            elif isinstance(value, bool):
                post_data[key] = not value
            elif isinstance(value, str):
                if value.startswith("$"):
                    post_data[key] = instance_ids[value[1:]]
                elif key.endswith("_rank"):
                    post_data[key] = chr(ord(value[0]) + 1)
                else:
                    post_data[key] = value + "_test_post_instance"

        response, status_code = post_instance(model_name, post_data)
        assert status_code == 201
        assert isinstance(response, dict)
        assert "id" in response
        assert isinstance(response["id"], str)
