from typing import Dict, TypedDict

# Model Configuration
MODEL_NAME = "gpt-5-nano"

# Budget Profile Types
class BudgetProfile(TypedDict):
    reasoning_effort: str # "minimal", "low", "medium", "high"
    max_output_tokens: int
    paths: int

# Budget Profiles Definition
BUDGET_PROFILES: Dict[str, BudgetProfile] = {
    "fast": {
        "reasoning_effort": "minimal",
        "max_output_tokens": 256,
        "paths": 1,
    },
    "normal": {
        "reasoning_effort": "low",
        "max_output_tokens": 512,
        "paths": 1,
    },
    "deep": {
        "reasoning_effort": "high",
        "max_output_tokens": 1024,
        "paths": 3,
    },
}

# Controller Output Type
class BudgetDecision(TypedDict):
    budget_label: str       # "fast" | "normal" | "deep"
    reasoning_effort: str
    max_output_tokens: int
    paths: int
    difficulty: str         # "easy" | "medium" | "hard"
