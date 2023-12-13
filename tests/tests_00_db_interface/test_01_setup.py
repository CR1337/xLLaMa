import pytest
from ..util.db_interaction import (
    create_database, drop_database, reset_database, populate_database
)


class TestDatabaseInterfaceSetup:

    @pytest.fixture(autouse=True)
    def method_wrapper(self):
        reset_database()
        populate_database()
        yield
        reset_database()
        populate_database()

    def test_drop_database(self):
        response, status_code = drop_database()
        assert status_code == 200
        assert response == {}

    def test_create_database(self):
        drop_database()
        response, status_code = create_database()
        assert status_code == 200
        assert response == {}

    def test_reset_database(self):
        response, status_code = reset_database()
        assert status_code == 200
        assert response == {}

    def test_populate_database(self):
        reset_database()
        response, status_code = populate_database()
        assert status_code == 200
        assert response == {}
