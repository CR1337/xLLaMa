from model import Prediction, FollowUp, FrameworkItem, Llm, PromptPart, \
    StopSequence, CodeSnippet, UserRating, Framework, FollowUpType, \
    PromptPartUsage, StopSequenceUsage, SymbolReference, \
    UserRatingType, BaseModel, SystemPrompt
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
    "symbol_references": SymbolReference,
    "system_prompts": SystemPrompt,
    "user_rating_types": UserRatingType,
    "user_ratings": UserRating
}

by_name_models: Dict[str, Type[BaseModel]] = {
    "follow_up_types": FollowUpType,
    "user_rating_types": UserRatingType,
    "llms": Llm,
    "frameworks": Framework,
    "framework_items": FrameworkItem,
    "system_prompts": SystemPrompt
}
