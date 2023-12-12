import pytest
from ..util.db_interaction import (
    reset_database, populate_database, get_instances, get_instance_by_name
)


class TestDatabaseInterfaceGet:

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
        ("user_rating_types", "sentiment")  # TODO: llm
    ])
    def test_get_instance_by_name(self, model_name: str, instance_name: str):
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

    def test_get_instance(self):
        ...

