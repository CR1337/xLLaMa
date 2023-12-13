import pytest
from ..util.db_interaction import (
    reset_database, populate_database, post_dummy_data, get_instance,
    delete_instance
)
from typing import Dict, Any


class TestDatabaseInterfaceGet:

    @pytest.fixture(scope='class')
    def instance_ids(self, method_wrapper: None) -> Dict[str, Any]:
        return post_dummy_data()

    @pytest.fixture(autouse=True, scope='class')
    def method_wrapper(self):
        reset_database()
        populate_database()
        yield
        reset_database()
        populate_database()

    @pytest.mark.parametrize("model_name", [
        "undefined_symbol_references",
        "symbol_definition_references",
        "symbol_references",
        "symbol_definitions",
        "symbol_definition_types",
        "code_snippets",
        "stop_sequence_usages",
        "stop_sequences",
        "prompt_part_usages",
        "prompt_parts",
        "follow_ups",
        "follow_up_types",
        "user_ratings",
        "@predictions",
        "predictions",
        "user_rating_types",
        "llms",
        "system_prompts",
        "framework_items",
        "frameworks"
    ])
    def test_delete_instance(
        self, model_name: str, instance_ids: Dict[str, Any]
    ):
        model_name_for_delete = (
            model_name[1:] if model_name.startswith("@") else model_name
        )
        response, status_code = delete_instance(
            model_name_for_delete, instance_ids[model_name]
        )
        assert status_code == 200
        assert isinstance(response, dict)
        assert response == {}
        response, status_code = get_instance(
            model_name, instance_ids[model_name]
        )
        assert status_code == 404
        assert isinstance(response, dict)
