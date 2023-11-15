import os


class Config:

    STREAM_RETRY_PERIOD: int = 3000  # ms
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    OLLAMA_ADDRESS: str = os.getenv('OLLAMA_ADDRESS')
    OLLAMA_PORT: int = int(os.getenv('OLLAMA_PORT'))


class Defaults:

    REPEAT_PENALTY: float = 1.1
    MAX_TOKENS: int = 256
    SEED: int = 0
    TEMPERATURE: float = 0.8
    TOP_P: float = 0.9
