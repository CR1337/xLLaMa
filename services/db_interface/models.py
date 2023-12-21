from model import Prediction, FollowUp, FrameworkItem, Llm, PromptPart, \
    StopSequence, CodeSnippet, UserRating, Framework, FollowUpType, \
    PromptPartUsage, StopSequenceUsage, SymbolDefinition, \
    SymbolDefinitionType, SymbolReference, SymbolDefinitionReference, \
    UndefinedSymbolReference, UserRatingType, BaseModel, SystemPrompt
from typing import Dict, Type

models: Dict[str, Type[BaseModel]] = {
    "code_snippets": CodeSnippet,
    "follow_up_types": FollowUpType,
    "follow_ups": FollowUp,
    "framework_items": FrameworkItem,
    "frameworks": Framework,
    "llms": Llm,
    "predictions": Prediction,
    "prompt_part_usages": PromptPartUsage,
    "prompt_parts": PromptPart,
    "stop_sequence_usages": StopSequenceUsage,
    "stop_sequences": StopSequence,
    "symbol_definition_references": SymbolDefinitionReference,
    "symbol_definition_types": SymbolDefinitionType,
    "symbol_definitions": SymbolDefinition,
    "symbol_references": SymbolReference,
    "system_prompts": SystemPrompt,
    "undefined_symbol_references": UndefinedSymbolReference,
    "user_rating_types": UserRatingType,
    "user_ratings": UserRating
}

by_name_models: Dict[str, Type[BaseModel]] = {
    "follow_up_types": FollowUpType,
    "symbol_definition_types": SymbolDefinitionType,
    "user_rating_types": UserRatingType,
    "llms": Llm,
    "frameworks": Framework,
    "framework_items": FrameworkItem
}
