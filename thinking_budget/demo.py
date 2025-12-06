import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from .controller import BudgetController
from .agent import ReasoningAgent

# Ensure env vars are loaded if this is the entry point
load_dotenv()

def run_single_question(
    question: str,
    importance: str = "normal",
) -> Dict[str, Any]:
    """
    Orchestrates the 2-Agent flow for a single question:
    1. BudgetController decides the budget.
    2. ReasoningAgent executes the answer using that budget.
    """
    
    # 1. Instantiate components
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
    client = OpenAI(api_key=api_key)
    controller = BudgetController(client)
    agent = ReasoningAgent(client)

    # 2. Agent 1 - BudgetController
    # decide_budget returns a BudgetDecision TypedDict
    budget = controller.decide_budget(question, importance)

    # 3. Agent 2 - ReasoningAgent
    # solve returns a dict with answer, usage, raw_outputs, tie_breaker_used
    result = agent.solve(question, budget)

    # 4. Return object
    return {
        "question": question,
        "importance": importance,
        "budget": budget,
        "answer": result["answer"],
        "usage": result["usage"],
        "tie_breaker_used": result.get("tie_breaker_used", False),
        "raw_outputs": result.get("raw_outputs", []),
    }
