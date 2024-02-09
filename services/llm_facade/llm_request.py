from abc import ABC, abstractmethod, abstractclassmethod, abstractclassproperty
from typing import Any, Dict, List
from db_interface import DbInterface


class LlmRequest(ABC):

    DEFAULT_REPEAT_PENALTY: float = 1.1
    DEFAULT_MAX_TOKENS: int = 256
    DEFAULT_SEED: int = 0
    DEFAULT_TEMPERATURE: float = 0.8
    DEFAULT_TOP_P: float = 0.9

    _repeat_penalty: float
    _max_tokens: int
    _seed: int
    _temperature: float
    _top_p: float

    _llm_id: str
    _framework_item_id: str
    _system_prompt_id: str | None
    _parent_follow_up_id: str | None
    _prompt_part_ids: List[str]
    _stop_sequence_ids: List[str] | None

    _llm: Dict[str, Any]
    _framework_item: Dict[str, Any]
    _system_prompt: Dict[str, Any] | None
    _parent_follow_up: Dict[str, Any] | None
    _prompt_parts: List[Dict[str, Any]]
    _stop_sequences: List[Dict[str, Any]] | None

    _prompt: str

    _text: str
    _token_amount: int
    _prediction: Dict[str, Any] | None

    def __init__(
        self,
        repeat_penalty: float | None,
        max_tokens: int | None,
        seed: int | None,
        temperature: float | None,
        top_p: float | None,
        llm_id: str | None,
        framework_item_id: str,
        system_prompt_id: str | None,
        parent_follow_up_id: str | None,
        prompt_part_ids: List[str],
        stop_sequence_ids: List[str] | None
    ):
        self._repeat_penalty = repeat_penalty or self.DEFAULT_REPEAT_PENALTY
        self._max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self._seed = seed or self.DEFAULT_SEED
        self._temperature = temperature or self.DEFAULT_TEMPERATURE
        self._top_p = top_p or self.DEFAULT_TOP_P

        self._llm_id = llm_id
        self._framework_item_id = framework_item_id
        self._system_prompt_id = system_prompt_id
        self._parent_follow_up_id = parent_follow_up_id
        self._prompt_part_ids = prompt_part_ids
        self._stop_sequence_ids = stop_sequence_ids

        self._llm = DbInterface.get_llm(self._llm_id)
        self._framework_item = DbInterface.get_framework_item(
            self._framework_item_id
        )
        self._system_prompt = (
            DbInterface.get_system_prompt(self._system_prompt_id)
            if self._system_prompt_id
            else None
        )
        self._parent_follow_up = (
            DbInterface.get_parent_follow_up(self._parent_follow_up_id)
            if self._parent_follow_up_id
            else None
        )
        self._prompt_parts = [
            DbInterface.get_prompt_part(prompt_part_id)
            for prompt_part_id in self._prompt_part_ids
        ]
        self._stop_sequences = (
            [
                DbInterface.get_stop_sequence(stop_sequence_id)
                for stop_sequence_id in self._stop_sequence_ids
            ]
            if self._stop_sequence_ids
            else None
        )

        self._prompt = "\n".join(p['text'] for p in self._prompt_parts)

        self._text = ""
        self._token_amount = 0
        self._prediction = None

    @abstractclassproperty
    def available(self) -> bool:
        raise NotImplementedError("abstract class property")

    @abstractclassproperty
    def model_names(cls) -> List[str]:
        raise NotImplementedError("abstract class method")

    @abstractclassmethod
    def uninstall_model(self, model: str):
        raise NotImplementedError("abstract class method")

    @classmethod
    def install_model(self, model: str, stream: bool):
        if stream:
            return self._install_model_stream(model)
        else:
            return self._install_model(model)

    def generate(self, stream: bool):
        if stream:
            return self._generate_stream()
        else:
            return self._generate()

    def has_model(self, model: str) -> bool:
        return model in self.model_names

    @abstractclassmethod
    def _install_model(cls, model_name: str):
        raise NotImplementedError("abstract class method")

    @abstractclassmethod
    def _install_model_stream(cls, model_name: str):
        raise NotImplementedError("abstract class method")

    @abstractmethod
    def _generate(self):
        raise NotImplementedError("abstract method")

    @abstractmethod
    def _generate_stream(self):
        raise NotImplementedError("abstract method")

    def _persist_db_objects(self):
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

        for position, prompt_part in enumerate(self._prompt_parts):
            DbInterface.post_prompt_part_usage(
                position,
                prompt_part['id'],
                self._prediction_id
            )

        if self._stop_sequences:
            for stop_sequence in self._stop_sequences:
                DbInterface.post_stop_sequence_usage(
                    stop_sequence['id'],
                    self._prediction_id
                )


REQUEST_CLASSES: List[LlmRequest] = []
