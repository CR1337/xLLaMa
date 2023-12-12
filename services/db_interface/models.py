from model import Prediction, FollowUp, FrameworkItem, Llm, PromptPart, \
    StopSequence, CodeSnippet, UserRating, Framework, FollowUpType, \
    PromptPartUsage, StopSequenceUsage, SymbolDefinition, \
    SymbolDefinitionType, SymbolReference, SymbolDefinitionReference, \
    UndefinedSymbolReference, UserRatingType, BaseModel, SystemPrompt
from typing import Dict, Type

models: Dict[str, Type[BaseModel]] = {
    "predictions": Prediction,
    "follow_ups": FollowUp,
    "follow_up_types": FollowUpType,
    "framework_items": FrameworkItem,
    "llms": Llm,
    "prompt_parts": PromptPart,
    "system_prompts": SystemPrompt,
    "stop_sequences": StopSequence,
    "code_snippets": CodeSnippet,
    "user_ratings": UserRating,
    "frameworks": Framework,
    "follow_up_types": FollowUpType,
    "prompt_part_usages": PromptPartUsage,
    "stop_sequence_usages": StopSequenceUsage,
    "symbol_definitions": SymbolDefinition,
    "symbol_definition_types": SymbolDefinitionType,
    "symbol_references": SymbolReference,
    "symbol_definition_references": SymbolDefinitionReference,
    "undefined_symbol_references": UndefinedSymbolReference,
    "user_rating_types": UserRatingType
}

by_name_models: Dict[str, Type[BaseModel]] = {
    "follow_up_types": FollowUpType,
    "symbol_definition_types": SymbolDefinitionType,
    "user_rating_types": UserRatingType,
    "llms": Llm
}
