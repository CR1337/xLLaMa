import requests


class TestLlmFacadeIndex:

    def test_index(self):
        response = requests.get("http://localhost:5001/")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert "message" in response.json()
