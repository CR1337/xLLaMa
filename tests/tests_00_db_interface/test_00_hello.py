from ..util.db_interaction import get_index


class TestDatabaseInterfaceIndex:

    def test_index(self):
        response, status_code = get_index()
        assert status_code == 200
        assert "message" in response
