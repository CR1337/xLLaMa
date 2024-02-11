from typing import Any, Callable, Dict, List, Iterator, Generator, Tuple
import os
from llm_request import LlmRequest
from threading import Thread
from queue import Queue, Empty
import requests
from concurrent.futures import ThreadPoolExecutor
from db_interface import DbInterface
import time
import json
from server_sent_events import ServerSentEvents
from ollama_scheduler import OllamaScheduler


class OllamaRequest(LlmRequest):
    """
    This represents a request to Ollama.
    It does (un)installing models and prediction.
    """

    OLLAMA_INSTANCES: int = int(os.getenv("OLLAMA_INSTANCES", 1))
    URLS: List[str] = [
        f'http://ollama_{i}:{int(os.getenv("OLLAMA_INTERNAL_PORT"))}'
        for i in range(OLLAMA_INSTANCES)
    ]
    STREAM_CHUNK_SIZE: int = 32

    @classmethod
    def available(cls) -> bool:
        return True

    @classmethod
    def model_names(cls) -> List[str]:
        responses = cls._parallel_ollama_request(
            requests.get,
            "/api/tags"
        )
        model_name_sets = [
            set(m['name'] for m in r.json()['models']) for r in responses
        ]
        return list(set.intersection(*model_name_sets))

    @classmethod
    def uninstall_model(cls, model_name: str):
        responses = cls._parallel_ollama_request(
            requests.delete,
            "/api/delete",
            json={"name": model_name}
        )
        statusses = (r.json().get('status') for r in responses)
        if not all(status == 'success' for status in statusses):
            return {}, 500
        return {}, 200

    @classmethod
    def _install_model(cls, model_name: str):
        responses = cls._parallel_ollama_request(
            requests.post,
            "/api/pull",
            {"name": model_name, "stream": False}
        )
        statusses = (r.json().get('status') for r in responses)
        if not all(status == 'success' for status in statusses):
            return {"status": "failed"}, 500
        llm = DbInterface.post_llm(model_name)
        return {"llm": llm['id']}, 200

    @classmethod
    def _parallel_ollama_request(
        cls,
        method: Callable,
        endpoint: str,
        json_payload: Dict[str, Any] | None = None
    ) -> Iterator[requests.Response]:
        with ThreadPoolExecutor(max_workers=cls.OLLAMA_INSTANCES) as executor:
            responses = executor.map(
                lambda i: method(
                    f"{cls.URLS[i]}{endpoint}",
                    json=json_payload
                ),
                range(cls.OLLAMA_INSTANCES)
            )
        return responses

    @classmethod
    def _install_model_stream(
        cls, model_name: str
    ) -> Generator[str, None, None]:
        def server_sent_event_generator():
            message_queues = [Queue() for _ in range(cls.OLLAMA_INSTANCES)]
            threads = [
                Thread(
                    target=cls._install_model_stream_on_single_instance,
                    args=(model_name, i, message_queues[i])
                )
                for i in range(cls.OLLAMA_INSTANCES)
            ]

            for thread in threads:
                thread.start()

            threads_alive = [True for _ in range(len(threads))]
            while any(threads_alive):
                for i, queue in enumerate(message_queues):
                    try:
                        event = queue.get(block=False)
                    except Empty:
                        pass
                    else:
                        yield event

                    if not threads[i].is_alive():
                        threads_alive[i] = False

                time.sleep(0.1)

            for thread in threads:
                thread.join()

        return server_sent_event_generator()

    @classmethod
    def _ollama_stream(
        cls,
        response: requests.Response,
        done_key: str,
        done_value: Any,
        done_handler: Callable[[int, Dict[str, Any]], Any],
        progress_handler: Callable[[int, Dict[str, Any]], Any]
    ) -> Generator[Any, None, None]:
        index = 0
        response_content = b""

        for chunk in response.iter_content(chunk_size=cls.STREAM_CHUNK_SIZE):
            if not chunk:
                continue
            response_content += chunk

            decoded_content = response_content.decode('utf-8')
            try:
                json_response = json.loads(decoded_content)
            except json.JSONDecodeError:
                continue

            if json_response[done_key] != done_value:
                yield progress_handler(index, json_response)
            else:
                yield done_handler(index, json_response)
                break

            index += 1
            response_content = b""

    @classmethod
    def _install_model_stream_on_single_instance(
        cls, model_name: str, ollama_index: int, message_queue: Queue
    ):
        def done_handler(index: int, json_response: Dict[str, Any]):
            llm = DbInterface.post_llm(model_name)
            event = ServerSentEvents.build_sse_data(
                "model_installation_success",
                json.dumps({
                    'llm': llm['id'],
                    'ollama_index': ollama_index
                }),
                index
            )
            message_queue.put(event)

        def progress_handler(index: int, json_response: Dict[str, Any]):
            event = ServerSentEvents.build_sse_data(
                "model_installation_progress",
                json.dumps({'ollama_index': ollama_index} | json_response),
                index
            )
            message_queue.put(event)

        with requests.Session().post(
            f"{cls.URLS[ollama_index]}/api/pull",
            json={'name': model_name, 'stream': True},
            headers=None,
            stream=True
        ) as response:
            for _ in cls._ollama_stream(
                response=response,
                done_key='status',
                done_value='success',
                done_handler=done_handler,
                progress_handler=progress_handler
            ):
                pass  # just consume the entire generator object

    def _generate(self) -> Tuple[Dict[str, Any], int]:
        with OllamaScheduler() as scheduler:
            response = requests.post(
                f"{self.URLS[scheduler.ollama_instance_index]}/api/generate",
                json=self._build_generation_request_body(stream=False)
            )

        json_response = response.json()
        self._text = json_response['response']
        self._token_amount = json_response['eval_count']

        self._persist_db_objects()

        return {'prediction': self._prediction_id}, 200

    def _generate_stream(self):
        def server_sent_event_generator():
            def done_handler(index: int, json_response: Dict[str, Any]) -> str:
                self._persist_db_objects()
                return ServerSentEvents.build_sse_data(
                    "generation_success",
                    json.dumps({'prediction': self._prediction_id}),
                    index
                )

            def progress_handler(
                index: int, json_response: Dict[str, Any]
            ) -> str:
                self._text += json_response['response']
                self._token_amount += 1
                return ServerSentEvents.build_sse_data(
                    "generation_progress",
                    json.dumps({'token': json_response['response']}),
                    index
                )

            with OllamaScheduler() as scheduler, requests.Session().post(
                f"{self.URLS[scheduler.ollama_instance_index]}/api/generate",
                json=self._build_generation_request_body(stream=True),
                headers=None,
                stream=True
            ) as response:
                for event in self._ollama_stream(
                    response=response,
                    done_key='done',
                    done_value=True,
                    done_handler=done_handler,
                    progress_handler=progress_handler
                ):
                    yield event

        return server_sent_event_generator()

    def _build_generation_request_body(self, stream: bool) -> Dict[str, Any]:
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
