from llm_request import LlmRequest, REQUEST_CLASSES
from openai import (
    OpenAI, AuthenticationError, APIConnectionError, ChatCompletion
)
import os
from typing import Dict, Any, Tuple, Generator, List
from server_sent_events import ServerSentEvents
import json


class OpenAiRequest(LlmRequest):

    _available: bool = True
    try:
        _client: OpenAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception:
        _available = False

    @classmethod
    @property
    def available(cls) -> bool:
        return cls._available

    @classmethod
    @property
    def model_names(cls) -> List[str]:
        if not cls._available:
            return []
        try:
            return [str(m) for m in cls._client.models.list()]
        except (AuthenticationError, APIConnectionError):
            return []

    @classmethod
    def uninstall_model(self, model: str):
        raise NotImplementedError(
            "OpenAI does not support model uninstallation"
        )

    @classmethod
    def _install_model(cls, model_name: str):
        raise NotImplementedError("OpenAI does not support model installation")

    @classmethod
    def _install_model_stream(cls, model_name: str):
        raise NotImplementedError("OpenAI does not support model installation")

    def _generate(self) -> Tuple[Dict[str, Any], int]:
        response = self._request_generation(stream=False)
        self._text = response.choices[0].message.content
        self._token_amount = response.usage.completion_tokens

        self._persist_db_objects()

        return {'prediction': self._prediction_id}, 200

    def _generate_stream(self) -> Generator[str, None, None]:
        def server_sent_event_generator():
            response = self._request_generation(stream=True)

            for i, event in enumerate(response):
                yield ServerSentEvents.build_sse_data(
                    "generation_progress",
                    json.dumps({
                        'token': event.choices[0].delta.content
                    }),
                    i
                )

                self._text += event.choices[0].delta.content
                self._token_amount += 1

            self._persist_db_objects()

            yield ServerSentEvents.build_sse_data(
                "generation_success",
                json.dumps({'prediction': self._prediction_id}),
                i + 1
            )

        return server_sent_event_generator

    def _request_generation(self, stream: bool) -> ChatCompletion:
        messages = []
        if self._system_prompt:
            messages.append({
                'role': 'system',
                'content': self._system_prompt['text']
            })
        messages.append({
            'role': 'user',
            'content': self._prompt
        })
        return self._client.chat.completions.create(
            model=self._llm['name'],
            messages=messages,
            stream=stream,
            frequency_penalty=self._repeat_penalty,
            max_tokens=self._max_tokens,
            seed=self._seed,
            temperature=self._temperature,
            top_p=self._top_p,
            stop=[s['text'] for s in self._stop_sequences or []]
        )


REQUEST_CLASSES.append(OpenAiRequest)
