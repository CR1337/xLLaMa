import pytest
from ..util.db_interaction import (
    reset_database, populate_database, get_instance,
    get_instance_by_name, post_instance
)


class TestDatabaseInterfaceErrors:

    @pytest.fixture(autouse=True)
    def method_wrapper(self):
        reset_database()
        populate_database()
        yield
        reset_database()
        populate_database()

    def test_get_non_existing_model_by_name(self):
        response, status_code = get_instance_by_name(
            "non_existing_model", "non_existing_instance"
        )
        assert status_code == 404
        assert isinstance(response, dict)

    def test_get_existing_model_by_non_existing_name(self):
        response, status_code = get_instance_by_name(
            "frameworks", "non_existing_instance"
        )
        assert status_code == 404
        assert isinstance(response, dict)

    def test_get_non_existing_model(self):
        response, status_code = get_instance(
            "non_existing_model", "non_existing_instance"
        )
        assert status_code == 404
        assert isinstance(response, dict)

    def test_not_null_constraint(self):
        response, status_code = post_instance(
            "frameworks", {"name": None}
        )
        assert status_code == 400
        assert isinstance(response, dict)

    def test_unique_constraint(self):
        response, status_code = post_instance(
            "frameworks", {"name": "test"}
        )
        assert status_code == 201
        assert isinstance(response, dict)
        response, status_code = post_instance(
            "frameworks", {"name": "test"}
        )
        assert status_code == 400
        assert isinstance(response, dict)
