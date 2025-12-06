from typing import Literal
from .config import BUDGET_PROFILES, BudgetDecision, MODEL_NAME

ImportanceLevel = Literal["low", "normal", "high"]
DifficultyLevel = Literal["easy", "medium", "hard"]

class BudgetController:
    def __init__(self, client):
        self.client = client

    def estimate_difficulty(self, question: str) -> DifficultyLevel:
        """
        Estimates the difficulty of a question.
        For v1, we use a simple heuristic + optional lightweight model call.
        Here we implement the lightweight model call as described in the requirements.
        """
        # Heuristic check first
        q_lower = question.lower()
        if "discount" in q_lower or "tax" in q_lower or "growth" in q_lower or "compound" in q_lower:
            # Likely medium or hard, let the model decide or default to medium/hard
            pass
        elif "*" in question or "+" in question or "times" in q_lower or "plus" in q_lower:
             # Likely easy
             pass

        # Lightweight classification call
        try:
            response = self.client.responses.create(
                model=MODEL_NAME,
                input=[
                    {"role": "system", "content": "Classify this question as one of: easy, medium, hard. Only output the label."},
                    {"role": "user", "content": f"Question: {question}"}
                ],
                max_output_tokens=16,
                reasoning={"effort": "minimal"}
            )
            label = response.output_text.strip().lower()
            if label in ["easy", "medium", "hard"]:
                return label
        except Exception as e:
            print(f"Warning: Difficulty estimation failed: {e}")
        
        # Fallback heuristics if model call fails or returns weird output
        if "compound" in q_lower or " YoY " in q_lower or "growth" in q_lower:
            return "hard"
        if "discount" in q_lower or "tax" in q_lower:
            return "medium"
        return "easy"

    def decide_budget(self, question: str, importance: ImportanceLevel) -> BudgetDecision:
        difficulty = self.estimate_difficulty(question)
        
        # Rule Table
        # difficulty \ importance | low      | normal   | high
        # ------------------------------------------------------
        # easy                    | fast     | fast     | normal
        # medium                  | fast     | normal   | deep
        # hard                    | normal   | deep     | deep

        if difficulty == "easy":
            if importance == "high":
                budget_label = "normal"
            else:
                budget_label = "fast"
        elif difficulty == "medium":
            if importance == "low":
                budget_label = "fast"
            elif importance == "normal":
                budget_label = "normal"
            else: # high
                budget_label = "deep"
        else: # hard
            if importance == "low":
                budget_label = "normal"
            else:
                budget_label = "deep"

        profile = BUDGET_PROFILES[budget_label]
        
        return {
            "budget_label": budget_label,
            "reasoning_effort": profile["reasoning_effort"],
            "max_output_tokens": profile["max_output_tokens"],
            "paths": profile["paths"],
            "difficulty": difficulty
        }
