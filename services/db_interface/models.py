from model import Prediction, FollowUp, FrameworkItem, Llm, PromptPart, \
    StopSequence, CodeSnippet, UserRating, Framework, FollowUpType, \
    PromptPartUsage, PromptPartType, StopSequenceUsage, SymbolDefinition, \
    SymbolDefinitionType, SymbolReference, SymbolDefinitionReference, \
    UndefinedSymbolReference, UserRatingType, BaseModel
from typing import Dict, Type

models: Dict[str, Type[BaseModel]] = {
    "predictions": Prediction,
    "follow_ups": FollowUp,
    "follow_up_types": FollowUpType,
    "framework_items": FrameworkItem,
    "llms": Llm,
    "prompt_parts": PromptPart,
    "stop_sequences": StopSequence,
    "code_snippets": CodeSnippet,
    "user_ratings": UserRating,
    "frameworks": Framework,
    "follow_up_types": FollowUpType,
    "prompt_part_usages": PromptPartUsage,
    "prompt_part_types": PromptPartType,
    "stop_sequence_usages": StopSequenceUsage,
    "symbol_definitions": SymbolDefinition,
    "symbol_definition_types": SymbolDefinitionType,
    "symbol_references": SymbolReference,
    "symbol_definition_references": SymbolDefinitionReference,
    "undefined_symbol_references": UndefinedSymbolReference,
    "user_rating_types": UserRatingType
}
