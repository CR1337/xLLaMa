import pytest
from ..util.db_interaction import (
    reset_database, populate_database, post_dummy_data, patch_instance,
    get_instance
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

    @pytest.mark.parametrize("model_name, key, value", [
        ("predictions", "text", "test"),
        ("follow_up_types", "name", "test"),
        ("framework_items", "name", "test"),
        ("llms", "name", "test"),
        ("prompt_parts", "text", "test"),
        ("system_prompts", "text", "test"),
        ("stop_sequences", "text", "test"),
        ("code_snippets", "code", "test"),
        ("user_ratings", "value", 42.0),
        ("frameworks", "name", "test"),
        ("prompt_part_usages", "position", 42),
        ("symbol_definitions", "symbol", "test"),
        ("symbol_definition_types", "name", "test"),
        ("symbol_references", "start_line", 42),
        ("undefined_symbol_references", "symbol", "test"),
        ("user_rating_types", "name", "test")
    ])
    def test_patch_instance(
        self,
        model_name: str,
        key: str,
        value: Any,
        instance_ids: Dict[str, Any]
    ):
        response, status_code = patch_instance(
            model_name, instance_ids[model_name], {key: value}
        )
        assert status_code == 200
        assert isinstance(response, dict)
        assert response == {}
        response, status_code = get_instance(
            model_name, instance_ids[model_name]
        )
        assert status_code == 200
        assert isinstance(response, dict)
        assert key in response
        assert response[key] == value
