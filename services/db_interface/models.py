from model import Prediction, FollowUp, FrameworkItem, Llm, PromptPart, \
    StopSequence, CodeSnippet, UserRating, Framework, FollowUpType, \
    PromptPartUsage, PromptPartType, StopSequenceUsage, SymbolDefinition, \
    SymbolDefinitionType, SymbolReference, SymbolDefinitionReference, \
    UndefinedSymbolReference, UserRatingType, BaseModel
from typing import Dict, Type

models: Dict[str, Type[BaseModel]] = {
    "prediction": Prediction,
    "follow_up": FollowUp,
    "follow_up_type": FollowUpType,
    "framework_item": FrameworkItem,
    "llm": Llm,
    "prompt_part": PromptPart,
    "stop_sequence": StopSequence,
    "code_snippet": CodeSnippet,
    "user_rating": UserRating,
    "framework": Framework,
    "follow_up_type": FollowUpType,
    "prompt_part_usage": PromptPartUsage,
    "prompt_part_type": PromptPartType,
    "stop_sequence_usage": StopSequenceUsage,
    "symbol_definition": SymbolDefinition,
    "symbol_definition_type": SymbolDefinitionType,
    "symbol_reference": SymbolReference,
    "symbol_definition_reference": SymbolDefinitionReference,
    "undefined_symbol_reference": UndefinedSymbolReference,
    "user_rating_type": UserRatingType
}
