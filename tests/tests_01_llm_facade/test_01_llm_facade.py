import pytest
from ..util.db_interaction import (
    post_instance, reset_database, populate_database, get_instance,
    get_instance_by_name
)
from ..util.llm_facade_interaction import (
    get_models, install_model, generate
)


class TestLlmFacade:

    @pytest.fixture()
    def model_name(self):
        return "llama2:7b"

    @pytest.fixture(autouse=True)
    def method_wrapper(self):
        reset_database()
        populate_database()
        yield
        reset_database()
        populate_database()

    def test_models(self):
        response, status_code = get_models()
        assert status_code == 200
        assert "models" in response
        assert isinstance(response["models"], list)
        for model in response["models"]:
            assert isinstance(model, str)

    def test_generate(self, model_name: str):
        models = get_models()[0]["models"]
        if model_name not in models:
            install_model(model_name)
        llm = get_instance_by_name("llms", model_name)[0]
        system_prompt_id = post_instance(
            "system_prompts",
            {"text": "You give short answers."}
        )[0]['id']
        prompt_part_id = post_instance(
            "prompt_parts",
            {"text": "Please repeat this word: 'Test'."}
        )[0]['id']
        framework_id = post_instance(
            "frameworks",
            {
                "name": "Test Framework",
                "url": "https://www.example.com"
            }
        )[0]['id']
        framework_item_id = post_instance(
            "framework_items",
            {
                "name": "test_item",
                "url": "https://www.example.com",
                "description": "This is a test item.",
                "source": "test_source",
                "framework": framework_id
            }
        )[0]['id']
        response, status_code = generate(
            llm['id'],
            framework_item_id,
            [prompt_part_id],
            {
                "max_tokens": 10,
                "temperature": 0.0,
                "top_p": 1,
                "system_prompt": system_prompt_id
            }
        )
        assert status_code == 200
        assert "prediction" in response
        assert isinstance(response["prediction"], str)

        prediction_id = response["prediction"]
        response, status_code = get_instance("predictions", prediction_id)
        assert status_code == 200
        assert isinstance(response, dict)
        assert "text" in response
        assert "test" in response["text"].lower()
