import statistics
import re
from typing import Any, Tuple, Optional, Dict
from .config import MODEL_NAME, BudgetDecision

class ReasoningAgent:
    def __init__(self, client):
        self.client = client

    def extract_number(self, text: str) -> Optional[float]:
        """Simple extraction of the last number in the text."""
        # Try to find the last number in the string
        # This regex handles simple floats and integers
        matches = re.findall(r'-?\d+(?:\.\d+)?', text.replace(',', ''))
        if matches:
            return float(matches[-1])
        return None

    def call_model(self, question: str, reasoning_effort: str, max_tokens: int) -> Tuple[Optional[float], str, Dict[str, Any]]:
        """Makes a single call to the model using the Responses API."""
        prompt = f"You are a precise numeric reasoner. Read the problem and return only the final numeric value, no explanation. Question: {question}"
        
        try:
            response = self.client.responses.create(
                model=MODEL_NAME,
                input=[{"role": "user", "content": prompt}],
                reasoning={"effort": reasoning_effort},
                max_output_tokens=max_tokens
            )
            content = response.output_text
            
            usage = {
                "total_tokens": response.usage.total_tokens,
                "completion_tokens": response.usage.output_tokens,
                "prompt_tokens": response.usage.input_tokens,
                "reasoning_tokens": response.usage.output_tokens_details.reasoning_tokens if response.usage.output_tokens_details else 0
            }
            
            return self.extract_number(content), content, usage
            
        except Exception as e:
            print(f"Error calling model: {e}")
            return None, str(e), {"total_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}

    def solve(self, question: str, budget: BudgetDecision) -> Dict[str, Any]:
        paths = budget["paths"]
        results = []
        total_usage = {"total_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}
        raw_outputs = []

        for _ in range(paths):
            val, raw_text, usage = self.call_model(question, budget["reasoning_effort"], budget["max_output_tokens"])
            results.append(val)
            raw_outputs.append(raw_text)
            
            # Aggregate usage
            total_usage["total_tokens"] += usage.get("total_tokens", 0)
            total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
            total_usage["reasoning_tokens"] += usage.get("reasoning_tokens", 0)

        # Aggregation Logic
        final_answer = None
        tie_breaker_used = False
        
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            final_answer = None
        elif len(valid_results) == 1:
            final_answer = valid_results[0]
        else:
            # Majority vote
            try:
                mode = statistics.mode(valid_results)
                final_answer = mode
            except statistics.StatisticsError:
                # No unique mode, take median
                final_answer = statistics.median(valid_results)
                tie_breaker_used = True

        return {
            "answer": final_answer,
            "raw_outputs": raw_outputs,
            "usage": total_usage,
            "tie_breaker_used": tie_breaker_used
        }
