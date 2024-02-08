import subprocess
from shutil import copyfile
from typing import List
import sys
import requests
import json

try:
    from tqdm import tqdm
except (ImportError, ModuleNotFoundError):

    class tqdm:
        def __init__(self, *args, **kwargs):
            pass

        def update(self, *args, **kwargs):
            pass

        def finish(self, *args, **kwargs):
            pass

        def refresh(self, *args, **kwargs):
            pass


CYAN: str = "\033[1;96m"
GREEN: str = "\033[1;92m"
RED: str = "\033[1;91m"
RESET_COLOR: str = "\033[0m"

LLM_FACADE_PORT: int = 5001
MODEL_INSTALLATION_ENDPOINT: str = "/model/install"
MODELS: List[str] = [
    "codellama:7b-instruct",
    "wizardcoder:13b-python",
    "llama2:7b"
]

STREAM_CHUNK_SIZE: int = 4096

is_local = "--local" in sys.argv
dash_local_suffix = "-local" if is_local else ""
dot_local_suffix = dash_local_suffix.replace("-", ".")


def print_color(text: str, color: str):
    print(f"{color}{text}{RESET_COLOR}")


def run_program(
    command: List[str],
    info_message: str,
    success_message: str,
    failure_message: str,
):
    print_color(info_message, CYAN)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            print(output.decode("utf-8").strip())

    _, stderr = process.communicate()

    if process.returncode != 0:
        print(stderr.decode("utf-8"))
        print_color(failure_message, RED)
        sys.exit(process.returncode)
    else:
        print_color(f"{success_message}\n", GREEN)


def copy_file(
    from_path: str,
    to_path: str,
    info_message: str,
    success_message: str,
    failure_message: str
):
    print_color(info_message, CYAN)
    try:
        copyfile(from_path, to_path)
    except FileNotFoundError:
        print_color(failure_message, RED)
        sys.exit(1)
    print_color(f"{success_message}\n", GREEN)


def ask_for_integer(
    prompt: str,
    min_value: int,
    max_value: int,
    default_value: int | None = None
) -> int:
    while True:
        answer = input(prompt)
        if answer == "" and default_value is not None:
            return default_value
        try:
            value = int(answer)
        except ValueError:
            print_color("Please enter an integer", RED)
            continue
        else:
            if min_value <= value <= max_value:
                return value
            else:
                print_color(
                    f"Please enter an integer between {min_value} and "
                    f"{max_value}",
                    RED
                )


def get_environment_key(filename: str, key: str) -> str:
    with open(filename, "r") as file:
        for line in file:
            if line.startswith(key):
                return line.split("=")[1].strip()


def set_environment_key(filename: str, key: str, value: str):
    with open(filename, "r") as file:
        lines = file.readlines()
    with open(filename, "w") as file:
        for line in lines:
            if line.startswith(key):
                file.write(f"{key}={value}\n")
            else:
                file.write(line)


def set_environment(gpu_ids: List[int]):
    print_color("Setting environment...", CYAN)
    set_environment_key(".env", "LOCAL", "1" if is_local else "0")
    if gpu_ids:
        set_environment_key(".env", "GPU0", str(gpu_ids[0]))
        set_environment_key(".env", "GPU1", str(gpu_ids[-1]))
    else:
        set_environment_key(".env", "GPU0", "0")
        set_environment_key(".env", "GPU1", "0")
    print_color("Successfully set environment\n", GREEN)


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
