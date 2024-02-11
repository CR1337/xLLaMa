import redis
import os
from typing import Callable


class OllamaScheduler:
    """
    This is used to assign Ollama workers to flask workers.
    See doc/xLLaMa_endpresentation.pdf
    """

    OLLAMA_INSTANCES: int = int(os.environ['OLLAMA_INSTANCES'])
    REDIS_KEY: str = 'ollama_usage'

    cache: redis.Redis = redis.Redis(
        host='cache',
        port=os.environ.get('CACHE_INTERNAL_PORT', 6379),
        decode_responses=True
    )

    cache.hset(REDIS_KEY, mapping={
        str(ollama_id): 0 for ollama_id in range(OLLAMA_INSTANCES)
    })

    _ollama_instance_index: int | None

    @property
    def ollama_instance_index(self) -> int | None:
        return self._ollama_instance_index

    def __init__(self):
        self._ollama_instance_index = None

    def _redis_atomic(
        self, func: Callable[[redis.client.Pipeline], None]
    ):
        while True:
            with self.cache.pipeline() as pipe:
                try:
                    pipe.watch(self.REDIS_KEY)
                    func(pipe)
                    pipe.execute()
                except redis.WatchError:
                    continue
                finally:
                    pipe.reset()
                    break

    def _allocate(self, pipe: redis.client.Pipeline):
        usage = pipe.hgetall(self.REDIS_KEY)
        min_usage_index = min(
            usage,
            key=lambda ollama_id: int(usage[ollama_id])
        )
        self._ollama_instance_index = int(min_usage_index)
        pipe.multi()
        pipe.hincrby(self.REDIS_KEY, min_usage_index, 1)

    def _free(self, pipe: redis.client.Pipeline):
        pipe.multi()
        pipe.hincrby(self.REDIS_KEY, self._ollama_instance_index, -1)

    def __enter__(self):
        self._redis_atomic(self._allocate)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._redis_atomic(self._free)
