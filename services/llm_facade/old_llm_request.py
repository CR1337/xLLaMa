from abc import ABC, abstractmethod, abstractclassmethod
from typing import Any, Dict, List, Tuple, Generator
from openai import (
    OpenAI, ChatCompletion, AuthenticationError, APIConnectionError
)
import requests
import json
import os
import threading
import time
from queue import Queue
from db_interface import DbInterface
from server_sent_events import ServerSentEvents
from concurrent.futures import ThreadPoolExecutor
from ollama_scheduler import OllamaScheduler


class LlmRequest(ABC):

    DEFAULT_REPEAT_PENALTY: float = 1.1
    DEFAULT_MAX_TOKENS: int = 256
    DEFAULT_SEED: int = 0
    DEFAULT_TEMPERATURE: float = 0.8
    DEFAULT_TOP_P: float = 0.9

    _repeat_penalty: float
    _max_tokens: int
    _seed: int | None
    _temperature: float
    _top_p: float

    _llm_id: str
    _framework_item_id: str
    _system_prompt_id: str | None
    _parent_follow_up_id: str | None

    _prompt_part_ids: List[str]
    _stop_sequence_ids: List[str] | None

    _prompt: str

    _text: str | None
    _token_amount: int | None
    _prediction: Dict[str, Any] | None

    _llm: Dict[str, Any]
    _framework_item: Dict[str, Any]
    _system_prompt: Dict[str, Any] | None
    _parent_follow_up: Dict[str, Any] | None

    _prompt_parts: List[Dict[str, Any]]
    _stop_sequences: List[Dict[str, Any]] | None

    def __init__(
        self,
        repeat_penalty: float,
        max_tokens: int,
        seed: int | None,
        temperature: float,
        top_p: float,
        llm: str,
        framework_item: str,
        system_prompt: str | None,
        parent_follow_up: str | None,
        prompt_parts: List[str],
        stop_sequences: List[str] | None
    ):
        self._repeat_penalty = (
            float(repeat_penalty)
            if repeat_penalty
            else self.DEFAULT_REPEAT_PENALTY
        )
        self._max_tokens = (
            int(max_tokens) if max_tokens else self.DEFAULT_MAX_TOKENS
        )
        self._seed = int(seed) if seed else self.DEFAULT_SEED
        self._temperature = (
            float(temperature) if temperature else self.DEFAULT_TEMPERATURE
        )
        self._top_p = float(top_p) if top_p else self.DEFAULT_TOP_P
        self._llm_id = llm
        self._framework_item_id = framework_item
        self._system_prompt_id = system_prompt
        self._parent_follow_up_id = parent_follow_up
        self._prompt_part_ids = prompt_parts
        self._stop_sequence_ids = stop_sequences

        self._text = ""
        self._token_amount = 0
        self._prediction_id = None

        self._llm = DbInterface.get_llm(llm)
        self._framework_item = DbInterface.get_framework_item(framework_item)
        self._system_prompt = (
            DbInterface.get_system_prompt(system_prompt)
            if system_prompt is not None
            else None
        )
        self._parent_follow_up = (
            DbInterface.get_follow_up(parent_follow_up)
            if parent_follow_up is not None
            else None
        )

        self._prompt_parts = [
            DbInterface.get_prompt_part(id) for id in self._prompt_part_ids
        ]
        self._stop_sequences = (
            [
                DbInterface.get_stop_sequence(id)
                for id in self._stop_sequence_ids
            ]
            if stop_sequences is not None
            else None
        )

        self._prompt = "\n".join([p['text'] for p in self._prompt_parts])

    @abstractclassmethod
    def model_names(cls) -> List[str]:
        raise NotImplementedError()

    @classmethod
    def has_model(cls, model: str) -> bool:
        return model in cls.model_names()

    @abstractmethod
    def generate(self) -> Tuple[Dict[str, Any], int]:
        raise NotImplementedError()

    @abstractmethod
    def generate_stream(self) -> Generator[str, None, None]:
        raise NotImplementedError()

    @abstractmethod
    def _translate_event(self, event: Any) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def _process_event(self, event: Any):
        raise NotImplementedError()

    def _server_sent_even_loop(
        self, response: Any
    ) -> Generator[str, None, None]:
        for i, event in enumerate(response):
            yield ServerSentEvents.build_sse_data(
                "generation_progress",
                self._translate_event(event),
                i
            )
            self._process_event(event)
        self._persist_generation()
        yield ServerSentEvents.build_sse_data(
            "generation_success",
            json.dumps({"prediction": self._prediction_id}),
            i + 1
        )

    def _persist_generation(self):
        self._persist_prediction()
        self._persist_prompt_part_usages()
        self._persist_stop_sequence_usages()

    def _persist_prediction(self) -> Dict[str, Any]:
        self._prediction_id = DbInterface.post_prediction(
            self._text,
            self._token_amount,
            self._repeat_penalty,
            self._max_tokens,
            self._seed,
            self._temperature,
            self._top_p,
            self._parent_follow_up_id,
            self._framework_item_id,
            self._llm_id,
            self._system_prompt_id
        )['id']

    def _persist_prompt_part_usages(self) -> List[Dict[str, Any]]:
        for position, prompt_part in enumerate(self._prompt_parts):
            DbInterface.post_prompt_part_usage(
                position,
                prompt_part['id'],
                self._prediction_id
            )

    def _persist_stop_sequence_usages(self) -> List[Dict[str, Any]]:
        if self._stop_sequences is not None:
            for stop_sequence in self._stop_sequences:
                DbInterface.post_stop_sequence_usage(
                    stop_sequence['id'], self._prediction_id
                )


class OllamaRequest(LlmRequest):

    OLLAMA_INSTANCES: int = int(os.environ['OLLAMA_INSTANCES'])

    URLS: List[str] = [
        f'http://ollama_{i}:{int(os.environ.get("OLLAMA_INTERNAL_PORT"))}'
        # f'http://localhost:{PORTS[i]}'
        for i in range(OLLAMA_INSTANCES)
    ]
    STREAM_CHUNK_SIZE: int = 32

    @classmethod
    def model_names(cls) -> List[str]:
        with ThreadPoolExecutor(max_workers=cls.OLLAMA_INSTANCES) as executor:
            responses = executor.map(
                lambda i: requests.get(f"{cls.URLS[i]}/api/tags"),
                range(cls.OLLAMA_INSTANCES)
            )
        model_name_sets = [
            set(m['name'] for m in r.json()['models']) for r in responses
        ]
        return list(set.intersection(*model_name_sets))

    @classmethod
    def install_model(cls, name: str) -> Tuple[Dict[str, Any], int]:
        with ThreadPoolExecutor(max_workers=cls.OLLAMA_INSTANCES) as executor:
            responses = executor.map(
                lambda i: requests.post(
                    f"{cls.URLS[i]}/api/pull",
                    json={"name": name, 'stream': False}
                ),
                range(cls.OLLAMA_INSTANCES)
            )
        statusses = [r.json().get('status') for r in responses]
        if not all(status == 'success' for status in statusses):
            return {"status": "failed"}, 500
        llm = DbInterface.post_llm(name)
        return {"llm": llm['id']}, 200

    @classmethod
    def uninstall_model(cls, name: str) -> Tuple[Dict[str, Any], int]:
        with ThreadPoolExecutor(max_workers=cls.OLLAMA_INSTANCES) as executor:
            responses = executor.map(
                lambda i: requests.delete(
                    f"{cls.URLS[i]}/api/delete",
                    json={"name": name}
                ),
                range(cls.OLLAMA_INSTANCES)
            )
        statusses = [r.json().get('status') for r in responses]
        if not all(status == 'success' for status in statusses):
            return {}, 500
        return {}, 200

    @classmethod
    def install_model_stream_single(
        cls, name: str, ollama_index: int, message_queue: Queue
    ) -> Generator[str, None, None]:
        response_content = b""
        with requests.Session().post(
            f"{cls.URLS[ollama_index]}/api/pull",
            json={"name": name, 'stream': True},
            headers=None,
            stream=True
        ) as response:
            index = 0
            for chunk in response.iter_content(
                chunk_size=cls.STREAM_CHUNK_SIZE
            ):
                if chunk:
                    response_content += chunk
                    decoded_content = response_content.decode('utf-8')
                    try:
                        json_response = json.loads(decoded_content)
                    except json.JSONDecodeError:
                        # Continue accumulating chunks
                        # until a complete JSON is formed
                        pass
                    else:
                        if json_response['status'] != 'success':
                            event = ServerSentEvents.build_sse_data(
                                "model_installation_progress",
                                json.dumps(
                                    json_response | {
                                        'ollama_index': ollama_index
                                    }
                                ),
                                index
                            )
                            message_queue.put(event)
                            index += 1
                        else:
                            llm = DbInterface.post_llm(name)
                            event = ServerSentEvents.build_sse_data(
                                "model_installation_success",
                                json.dumps({
                                    "llm": llm['id'],
                                    'ollama_index': ollama_index
                                }),
                                index
                            )
                            message_queue.put(event)
                            break
                        response_content = b""

    @classmethod
    def install_model_stream_all(cls, name: str) -> Generator[str, None, None]:
        message_queues = [Queue() for _ in range(cls.OLLAMA_INSTANCES)]
        threads = [threading.Thread(
            target=cls.install_model_stream_single,
            args=(name, i, message_queues[i])
        ) for i in range(cls.OLLAMA_INSTANCES)]

        for thread in threads:
            thread.start()

        alive_threads = [True for _ in range(len(threads))]
        while any(alive_threads):
            for i, queue in enumerate(message_queues):
                try:
                    event = queue.get(block=False)
                except Exception:
                    pass
                else:
                    yield event
                if not threads[i].is_alive():
                    alive_threads[i] = False
            time.sleep(0.1)

        for thread in threads:
            thread.join()

    @classmethod
    def install_model_stream(cls, name: str) -> Generator[str, None, None]:
        def server_sent_event_generator():
            for event in cls.install_model_stream_all(name):
                yield event
        return server_sent_event_generator()

    def _build_generate_request_body(self, stream: bool) -> Dict[str, Any]:
        request_body = {
            'model': self._llm['name'],
            'prompt': self._prompt,
            'stream': stream,
            'options': {
                'repeat_penalty': self._repeat_penalty,
                'num_predict': self._max_tokens,
                'temperature': self._temperature,
                'top_p': self._top_p
            }
        }
        if self._seed:
            request_body['options']['seed'] = self._seed
        if self._system_prompt:
            request_body['system'] = self._system_prompt['text']
        if self._stop_sequences:
            request_body['options']['stop'] = [
                s['text'] for s in self._stop_sequences
            ]
        return request_body

    def generate(self) -> Tuple[Dict[str, Any], int]:
        request_body = self._build_generate_request_body(stream=False)

        with OllamaScheduler() as ollama_scheduler:
            response = requests.post(
                f"{self.URLS[ollama_scheduler.ollama_instance_index]}"
                "/api/generate",
                json=request_body
            )

        self._text = response.json()['response']
        self._token_amount = response.json()['eval_count']
        self._persist_generation()
        return {'prediction': self._prediction_id}, 200

    def _generate_event(self, json_event: Dict[str, Any], index: int) -> str:
        return ServerSentEvents.build_sse_data(
            event=(
                "generation_success"
                if json_event['done']
                else "generation_progress"
            ),
            data=(
                json.dumps({'prediction': self._prediction_id})
                if json_event['done']
                else json.dumps({'token': json_event['response']})
            ),
            id=index
        )

    def generate_stream(self) -> Generator[str, None, None]:
        def server_sent_event_generator():
            response_content = b""
            with OllamaScheduler() as ollama_scheduler:
                with requests.Session().post(
                    f"{self.URLS[ollama_scheduler.ollama_instance_index]}"
                    "/api/generate",
                    json=self._build_generate_request_body(stream=True),
                    headers=None,
                    stream=True
                ) as response:
                    index = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            response_content += chunk
                            decoded_content = response_content.decode('utf-8')
                            try:
                                json_response = json.loads(decoded_content)
                            except json.JSONDecodeError:
                                # Continue accumulating chunks
                                # until a complete JSON is formed
                                pass
                            else:
                                print(json_response, flush=True)
                                if json_response['done']:
                                    self._persist_generation()
                                else:
                                    self._text += json_response[
                                        'response'
                                    ]
                                    self._token_amount += 1
                                yield self._generate_event(
                                    json_response, index
                                )
                                if json_response['done']:
                                    break
                                index += 1
                                response_content = b""
        return server_sent_event_generator()

    def _translate_event(self, event: Any) -> Dict[str, Any]:
        print("EVENT:", event, flush=True)
        return json.dumps({
            'token': json.loads(event)['response'],
        })

    def _process_event(self, event: Any):
        self._text += json.loads(event)['response']
        self._token_amount += 1


class OpenAiRequest(LlmRequest):

    try:
        client: OpenAI = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    except Exception:
        available = False
    else:
        available = True

    @classmethod
    def model_names(cls) -> List[str]:
        try:
            return [str(m) for m in cls.client.models.list()]
        except (AuthenticationError, APIConnectionError):
            return []

    def _request_generation(self, stream: bool) -> ChatCompletion:
        messages = []
        if self._system_prompt:
            messages.append({
                'role': 'system',
                'content': self._system_prompt['text'],
            })
        messages.append({
            'role': 'user',
            'content': self._prompt
        })
        return self.client.chat.completions.create(
            model=self._llm['name'],
            messages=messages,
            stream=stream,
            frequency_penalty=self._repeat_penalty,
            max_tokens=self._max_tokens,
            seed=self._seed,
            temperature=self._temperature,
            top_p=self._top_p,
            stop=[s['text'] for s in self._stop_sequences]
        )

    def generate(self) -> Tuple[Dict[str, Any], int]:
        response = self._request_generation(stream=False)
        self._text = response.choices[0].message.content
        self._token_amount = response.usage.completion_tokens
        self._persist_generation()
        return {'prediction': self._prediction_id}, 200

    def generate_stream(self) -> Generator[str, None, None]:
        def server_sent_event_generator():
            response = self._request_generation(stream=True)
            for event in self._server_sent_even_loop(response):
                yield event
        return server_sent_event_generator()

    def _translate_event(self, event: Any) -> Dict[str, Any]:
        return json.dumps({
            'token': event.choices[0].delta.content,
        })

    def _process_event(self, event: Any):
        self._text += event.choices[0].delta.content
        self._token_amount += 1


REQUEST_CLASSES: List[LlmRequest] = [OllamaRequest, OpenAiRequest]
