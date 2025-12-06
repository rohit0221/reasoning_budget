import os
import time
from typing import Generator, Dict, Any
from openai import OpenAI
from ..controller import BudgetController
from ..agent import ReasoningAgent
from ..config import BUDGET_PROFILES

def run_single_question_verbose(
    question: str,
    importance: str = "normal",
) -> Generator[Dict[str, Any], None, None]:
    """
    Generator that yields events for each step of the thinking process.
    """
    
    yield {
        "step": "INIT",
        "message": "Initializing Agents...",
        "timestamp": time.time()
    }
    time.sleep(0.5) # UX Loading

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    controller = BudgetController(client)
    agent = ReasoningAgent(client)

    # --- Agent 1: Budget Controller ---
    yield {
        "step": "CONTROLLER_START",
        "message": "Agent 1 (Controller) analyzing request...",
        "type": "agent_action",
        "agent": "controller",
        "details": {"question": question, "user_importance": importance}
    }
    time.sleep(0.8)

    # 1. Difficulty Estimation
    yield {
        "step": "DIFFICULTY_ESTIMATION_START",
        "message": "Estimating question difficulty...",
        "type": "sub_process"
    }
    
    # We peek into the controller's logic (simulated for verbose display, then call actual)
    # The actual controller does this internally, but we'll show the UI what's happening
    difficulty = controller.estimate_difficulty(question)
    
    yield {
        "step": "DIFFICULTY_ESTIMATION_END",
        "message": f"Difficulty classified as: {difficulty.upper()}",
        "type": "decision",
        "result": difficulty
    }
    time.sleep(0.5)

    # 2. Budget Decision
    yield {
        "step": "MATRIX_LOOKUP",
        "message": "Consulting Decision Matrix (Difficulty vs Importance)...",
        "type": "logic_lookup",
        "details": {
            "row (Difficulty)": difficulty,
            "col (Importance)": importance
        }
    }
    time.sleep(0.6)

    budget = controller.decide_budget(question, importance)
    
    yield {
        "step": "BUDGET_FINALIZED",
        "message": f"Budget Profile Selected: {budget['budget_label'].upper()}",
        "type": "milestone",
        "data": budget
    }
    time.sleep(0.5)

    # --- Agent 2: Reasoning Agent ---
    yield {
        "step": "AGENT_START",
        "message": f"Agent 2 (Reasoning) activating with {budget['budget_label'].upper()} profile...",
        "type": "agent_action",
        "agent": "reasoner"
    }

    yield {
        "step": "API_PREPARATION",
        "message": "Constructing OpenAI API Payload...",
        "type": "technical_detail",
        "details": {
            "model": "gpt-5-nano",
            "reasoning_effort": budget['reasoning_effort'],
            "max_output_tokens": budget['max_output_tokens'],
            "paths": budget['paths']
        }
    }
    time.sleep(0.8)

    # 3. Execution
    if budget['paths'] > 1:
        yield {
            "step": "PARALLEL_EXECUTION",
            "message": f"Spawning {budget['paths']} parallel reasoning paths...",
            "type": "processing"
        }
    else:
         yield {
            "step": "SINGLE_EXECUTION",
            "message": "Executing single reasoning path...",
            "type": "processing"
        }

    start_time = time.time()
    result = agent.solve(question, budget)
    duration = time.time() - start_time

    yield {
        "step": "MODEL_RESPONSE",
        "message": f"Received response in {duration:.2f}s",
        "type": "success",
        "details": {
            "usage": result['usage'],
            "raw_answer": str(result['answer'])
        }
    }

    if result.get("tie_breaker_used"):
         yield {
            "step": "AGGREGATION",
            "message": "Tie-breaker used! calculating median of results.",
            "type": "alert"
        }

    # Final Result
    yield {
        "step": "COMPLETE",
        "message": "Process Complete",
        "timestamp": time.time(),
        "final_payload": {
            "question": question,
            "importance": importance,
            "budget": budget,
            "answer": result["answer"],
            "usage": result["usage"]
        }
    }
