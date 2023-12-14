import requests
from tests.util.environment import environment
from typing import Any, Dict, Tuple


CODE_ANALYZER_HOST = '127.0.0.1'
CODE_ANALYZER_PORT = environment['CODE_ANALYZER_EXTERNAL_PORT']
CODE_ANALYZER_URL = f'http://{CODE_ANALYZER_HOST}:{CODE_ANALYZER_PORT}'

TEST_PREDICTION_TEXT_FILENAME: str = "tests/util/test_prediction.txt"
with open(TEST_PREDICTION_TEXT_FILENAME, "r") as file:
    TEST_PREDICTION_TEXT = file.read()


def analyze_prediction(prediction_id: str) -> Tuple[Dict[str, Any], int]:
    response = requests.post(
        f'{CODE_ANALYZER_URL}/analyze-prediction',
        json={"prediction": prediction_id}
    )
    return response.json(), response.status_code
