from abc import ABC, abstractmethod, abstractclassmethod
from typing import Dict, List, Tuple
from llm_response import (
    LlmResponse, OllamaResponseStream, OpenAiResponseStream
)
from openai import OpenAI, ChatCompletion
from datetime import datetime
import requests
import json
from server_sent_events import ServerSentEvents
from config import Config, Defaults


open_ai_client: OpenAI = OpenAI(api_key=Config.OPENAI_API_KEY)

ollama_address: str = Config.OLLAMA_ADDRESS
ollama_port: int = Config.OLLAMA_PORT
ollama_url: str = f'http://{ollama_address}:{ollama_port}'


class LlmRequest(ABC):

    @abstractclassmethod
    def models(cls) -> List[str]:
        raise NotImplementedError()

    @classmethod
    def has_model(cls, model: str) -> bool:
        return model in cls.models()

    _model: str
    _prompt: str
    _system_prompt: str | None
    _repeat_penalty: float
    _max_tokens: int
    _seed: int | None
    _temperature: float
    _top_p: float
    _stop: List[str] | None

    def __init__(
        self,
        model: str,
        prompt: str,
        system_prompt: str | None,
        repeat_penalty: float,
        max_tokens: int,
        seed: int | None,
        temperature: float,
        top_p: float,
        stop: List[str] | None
    ):
        self._model = model
        self._prompt = prompt
        self._system_prompt = system_prompt
        self._repeat_penalty = repeat_penalty
        self._max_tokens = max_tokens
        self._seed = seed
        self._temperature = temperature
        self._top_p = top_p
        self._stop = stop

    @abstractmethod
    def generate(self):
        raise NotImplementedError()

    @abstractmethod
    def generate_stream(self):
        raise NotImplementedError()


class OpenAiRequest(LlmRequest):

    @classmethod
    def models(cls) -> List[str]:
        return [str(m) for m in open_ai_client.models.list()]

    def _make_raw_response(self, stream: bool) -> ChatCompletion:
        messages = []
        if self._system_prompt:
            messages.append({
                'role': 'system',
                'content': self._system_prompt
            })
        messages.append({
            'role': 'user',
            'content': self._prompt
        })
        return open_ai_client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=stream,
            frequency_penalty=self._repeat_penalty,
            max_tokens=self._max_tokens,
            seed=self._seed,
            temperature=self._temperature,
            top_p=self._top_p,
            stop=self._stop
        )

    def generate(self) -> LlmResponse:
        response = self._make_raw_response(False)
        return LlmResponse(
            response.choices[0].message.content,
            datetime.fomtimestamp(response.created).isoformat(),
            response.usage.completion_tokens,
        )

    def generate_stream(self) -> OpenAiResponseStream:
        stream = self._make_raw_response(True)

        def event_generator():
            for event in stream:
                yield event

        return OpenAiResponseStream(event_generator())


class OllamaRequest(LlmRequest):

    STREAM_CHUNK_SIZE: int = 32

    @classmethod
    def models(cls) -> List[str]:
        response = requests.get(f'{ollama_url}/api/tags')
        return [m.get('name') for m in response.json()['models']]

    @classmethod
    def install_model(
        cls, model: str, stream: bool
    ) -> Tuple[Dict[str, str], int]:
        if stream:
            session = requests.Session()

            def sse_generator():
                with session.post(
                    f'{ollama_url}/api/pull',
                    json={'name': model, 'stream': True},
                    headers=None,
                    stream=True
                ) as response:
                    for i, event in enumerate(
                        response.iter_lines(chunk_size=cls.STREAM_CHUNK_SIZE)
                    ):
                        yield ServerSentEvents.build_sse_data(
                            "model_installation_progress",
                            event,
                            i,
                            Defaults.STREAM_RETRY_PERIOD
                        )

            return sse_generator()
        else:
            response = requests.post(f'{ollama_url}/api/pull', json={
                'name': model, 'stream': False
            })
            return response.json(), response.status_code

    def _build_body(self, stream: bool) -> dict:
        body = {
            'model': self._model,
            'prompt': self._prompt,
            'stream': stream,
            'options': {
                'repeat_penalty': self._repeat_penalty,
                'num_predict': self._max_tokens,
                'temperature': self._temperature,
                'top_p': self._top_p
            }
        }
        if self._system_prompt:
            body['system'] = self._system_prompt
        if self._seed:
            body['options']['seed'] = self._seed
        if self._stop:
            body['options']['stop'] = self._stop
        return body

    def generate(self) -> LlmResponse:
        body = self._build_body(False)
        response = requests.post(f'{ollama_url}/api/generate', json=body)
        return LlmResponse(
            content=response.json()['response'],
            created_at=response.json()['created_at'],
            token_count=response.json()['eval_count']
        )

    def generate_stream(self) -> OllamaResponseStream:
        session = requests.Session()

        def event_generator():
            with session.post(
                f'{ollama_url}/api/generate',
                json=self._build_body(True),
                stream=True
            ) as response:
                for event in response.iter_lines(
                    chunk_size=self.STREAM_CHUNK_SIZE
                ):
                    yield json.loads(event)

        return OllamaResponseStream(event_generator)
