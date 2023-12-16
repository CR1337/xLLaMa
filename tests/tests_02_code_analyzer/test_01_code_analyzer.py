import pytest
from ..util.db_interaction import (
    post_instance, reset_database, populate_database, get_instance
)
from ..util.code_analyzer_interaction import (
    analyze_prediction, TEST_PREDICTION_TEXT
)
from typing import Any, Dict


class TestCodeAnalyzer:

    @pytest.fixture(autouse=True)
    def method_wrapper(self):
        reset_database()
        populate_database()
        yield
        reset_database()
        populate_database()

    def test_analyze_prediction(self):
        llm_id = post_instance(
            "llms", {"name": "test_llm"}
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
        prediction_id = post_instance(
            "predictions",
            {
                "text": TEST_PREDICTION_TEXT,
                "token_amount": 100,
                "repeat_penalty": 0.5,
                "max_tokens": 100,
                "seed": 0,
                "temperature": 0.5,
                "top_p": 1,
                "parent_follow_up": None,
                "framework_item": framework_item_id,
                "llm": llm_id,
                "system_prompt": None
            }
        )[0]['id']

        response, status_code = analyze_prediction(prediction_id)

        assert status_code == 200
        assert "code_snippets" in response
        assert len(response["code_snippets"]) == 2

        code_snippet_ids = response["code_snippets"]
        assert isinstance(code_snippet_ids, list)
        assert isinstance(code_snippet_ids[0], str)
        assert isinstance(code_snippet_ids[1], str)

        code_snippet_0, status_code = get_instance(
            "code_snippets", code_snippet_ids[0]
        )
        assert status_code == 200

        code_snippet_1, status_code = get_instance(
            "code_snippets", code_snippet_ids[1]
        )
        assert status_code == 200

        for code_snippet in (code_snippet_0, code_snippet_1):
            assert "code" in code_snippet
            assert code_snippet["code"] in TEST_PREDICTION_TEXT
            assert "start_line" in code_snippet
            assert "end_line" in code_snippet

            for column_name in (
                "raw_loc", "raw_lloc", "raw_sloc", "raw_comments", "raw_multi",
                "raw_single_comments", "raw_blank", "halstead_h1",
                "halstead_h2", "halstead_N1", "halstead_N2"
            ):
                assert column_name in code_snippet
                assert isinstance(code_snippet[column_name], int)

            for column_name in (
                "halstead_length",
                "halstead_volume", "halstead_difficulty", "halstead_effort",
                "halstead_time", "halstead_bugs",
                "cyclomatic_complexity_score", "maintainability_index_score",
            ):
                assert column_name in code_snippet
                assert isinstance(code_snippet[column_name], float)

            assert "cyclomatic_complexity_rank" in code_snippet
            assert code_snippet["cyclomatic_complexity_rank"] in (
                "A", "B", "C", "D", "E", "F"
            )
            assert "maintainability_index_rank" in code_snippet
            assert code_snippet["maintainability_index_rank"] in (
                "A", "B", "C"
            )
            assert "prediction" in code_snippet
            assert code_snippet["prediction"] == prediction_id

        self._check_code_snippet_0(code_snippet_0)
        self._check_code_snippet_1(code_snippet_1)

    def _check_code_snippet_0(self, code_snippet: Dict[str, Any]):
        assert code_snippet["start_line"] == 3
        assert code_snippet["end_line"] == 13
        # TODO: check symbol definitions and references

    def _check_code_snippet_1(self, code_snippet: Dict[str, Any]):
        assert code_snippet["start_line"] == 19
        assert code_snippet["end_line"] == 25
        # TODO: check symbol definitions and references
