from dataclasses import dataclass
from typing import Any, Dict, Generator
from abc import ABC, abstractmethod
from datetime import datetime
from config import Config
from server_sent_events import ServerSentEvents
import json


@dataclass
class LlmResponse:

    content: str
    created_at: str
    token_count: int

    def to_json(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'created_at': self.created_at,
            'token_count': self.token_count
        }


class LlmResponseStream(ABC):

    _done: bool

    _content: str
    _token_count: int

    _event_generator: Generator[str, None, None]

    def __init__(self, event_generator: Generator[str, None, None]):
        self._done = False
        self._content = ""
        self._token_count = 0
        self._event_generator = event_generator

    @abstractmethod
    def _handle_event(self, event: Dict[str, Any]):
        raise NotImplementedError()

    @abstractmethod
    def _extract_created_at(self, event: Dict[str, Any]) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _extract_token(self, event: Dict[str, Any]) -> str:
        raise NotImplementedError()

    def build_sse(self, created_at: str, token: str, id_: int) -> str:
        if self._done:
            data = {
                'content': self._content,
                'created_at': created_at,
                'done': self._done,
                'token_count': self._token_count
            }
        else:
            data = {
                'token': token,
                'created_at': created_at,
                'done': self._done
            }
        return ServerSentEvents.build_sse_data(
            'token_generated',
            json.dumps(data),
            id_,
            Config.STREAM_RETRY_PERIOD
        )

    def sse_generator(self) -> Generator[str, None, None]:
        for i, event in enumerate(self._event_generator()):
            self._handle_event(event)
            created_at = self._extract_created_at(event)
            token = self._extract_token(event)
            yield self.build_sse(created_at, token, i)


class OpenAiResponseStream(LlmResponseStream):

    def _handle_event(self, event: Dict[str, Any]):
        if event.choices[0].finish_reason is not None:
            self._done = True
        else:
            self._content += event.choices[0].delta.content
            self._token_count += 1

    def _extract_created_at(self, event: Dict[str, Any]) -> str:
        return datetime.fromtimestamp(event.created).isoformat()

    def _extract_token(self, event: Dict[str, Any]) -> str:
        return event.choices[0].delta.content


class OllamaResponseStream(LlmResponseStream):

    def _handle_event(self, event: Dict[str, Any]):
        if event['done']:
            self._done = True
        else:
            self._content += event['response']
            self._token_count += 1

    def _extract_created_at(self, event: Dict[str, Any]) -> str:
        return event['created_at']

    def _extract_token(self, event: Dict[str, Any]) -> str:
        return event['response']
