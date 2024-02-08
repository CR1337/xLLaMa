import requests
from tqdm import tqdm
import json
import sys
from bin._util import (
    CYAN,
    GREEN,
    RED,
    LLM_FACADE_PORT,
    MODEL_INSTALLATION_ENDPOINT,
    STREAM_CHUNK_SIZE,
    print_color
)


class ProgressBar:

    _description: str
    _maximum: int
    _value: int
    _bar: tqdm

    def __init__(self, description: str, maximum: int):
        self._description = description
        self._maximum = maximum
        self._value = 0
        self._bar = tqdm(
            total=self._maximum,
            desc=self._description,
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"
        )

    def _refresh(self):
        self._bar.refresh()

    def update(self, value: int):
        self._value = value
        self._bar.update(self._value)
        self._refresh()

    def finish(self):
        self.update(self._maximum)


def post_request(
    port: int,
    endpoint: str,
    info_message: str,
    success_message: str,
    failure_message: str
):
    print_color(info_message, CYAN)
    try:
        response = requests.post(f"http://localhost:{port}/{endpoint}")
    except requests.exceptions.ConnectionError:
        print_color(failure_message)
        sys.exit(1)
    else:
        if response.status_code != 200:
            print_color(failure_message, RED)
            sys.exit(1)
        else:
            print_color(f"{success_message}\n", GREEN)


def install_model_request(
    model_name: str,
    info_message: str,
    success_message: str,
    failure_message: str
):
    print_color(info_message, CYAN)
    url = f"http://localhost:{LLM_FACADE_PORT}{MODEL_INSTALLATION_ENDPOINT}"
    url += f"?model={model_name}"
    response_content = b""
    try:
        with requests.Session().get(
            url,
            stream=True,
            headers={"Connection": "keep-alive"}
        ) as response:
            current_status = None
            progress_bar = None

            for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
                if not chunk:
                    continue
                response_content += chunk
                if not chunk.endswith(b"\n\n"):
                    continue

                lines = response_content.decode("utf-8").split("\n")
                event = lines[0].split(": ")[1]

                if event == "model_installation_progress":
                    data = json.loads(lines[1].split(": ")[1])
                    if data['status'] != current_status:
                        current_status = data['status']
                        if progress_bar:
                            progress_bar.finish()
                        progress_bar = ProgressBar(
                            current_status, data.get('total', 1)
                        )
                    else:
                        progress_bar.update(data.get('completed', 1))

                elif event == "model_installation_success":
                    if progress_bar:
                        progress_bar.finish()
                    break
    except Exception:
        print_color(failure_message, RED)
        sys.exit(1)
    else:
        print_color(f"{success_message}\n", GREEN)
