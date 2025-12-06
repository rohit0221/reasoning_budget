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
    time.sleep(1.0) # UX Loading

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    controller = BudgetController(client)
    agent = ReasoningAgent(client)

    # --- Agent 1: Budget Controller ---
    yield {
        "step": "CONTROLLER_START",
        "message": "ACTIVATING AGENT 1: BUDGET CONTROLLER",
        "type": "agent_action",
        "agent": "controller",
        "details": {"role": "Controller", "task": "Assess Difficulty & Allocate Budget", "inputs": {"question": question, "importance": importance}}
    }
    time.sleep(2.0)

    # 1. Difficulty Estimation
    yield {
        "step": "DIFFICULTY_ESTIMATION_START",
        "message": "Analyzing question complexity...",
        "type": "sub_process"
    }
    time.sleep(1.5)
    
    # We peek into the controller's logic (simulated for verbose display, then call actual)
    difficulty = controller.estimate_difficulty(question)
    
    yield {
        "step": "DIFFICULTY_ESTIMATION_END",
        "message": f"Difficulty determined: {difficulty.upper()}",
        "type": "decision",
        "result": difficulty
    }
    time.sleep(1.5)

    # 2. Budget Decision
    yield {
        "step": "MATRIX_LOOKUP",
        "message": f"Mapping Difficulty ({difficulty}) + Importance ({importance}) to Budget...",
        "type": "logic_lookup",
        "details": {
            "row": difficulty,
            "col": importance
        }
    }
    time.sleep(1.5)

    budget = controller.decide_budget(question, importance)
    
    yield {
        "step": "BUDGET_FINALIZED",
        "message": f"Selected Budget Profile: {budget['budget_label'].upper()}",
        "type": "milestone",
        "data": budget
    }
    time.sleep(2.0)

    # --- Agent 2: Reasoning Agent ---
    yield {
        "step": "AGENT_START",
        "message": "ACTIVATING AGENT 2: REASONING ENGINE",
        "type": "agent_action",
        "agent": "reasoner",
         "details": {"role": "Reasoner", "task": "Execute Logic & Solve", "config": budget}
    }
    time.sleep(2.0)

    yield {
        "step": "API_PREPARATION",
        "message": "Configuring OpenAI API Request...",
        "type": "technical_detail",
        "details": {
            "model": "gpt-5-nano",
            "reasoning_effort": budget['reasoning_effort'],
            "max_output_tokens": budget['max_output_tokens'],
            "paths": budget['paths']
        }
    }
    time.sleep(1.5)

    # 3. Execution
    msg = "Executing single reasoning path..."
    if budget['paths'] > 1:
        msg = f"Spawning {budget['paths']} parallel reasoning paths for validation..."

    yield {
        "step": "EXECUTION_START",
        "message": msg,
        "type": "processing"
    }
    time.sleep(1.5)

    start_time = time.time()
    result = agent.solve(question, budget)
    duration = time.time() - start_time

    yield {
        "step": "MODEL_RESPONSE",
        "message": f"Received model response in {duration:.2f}s",
        "type": "success",
        "details": {
            "usage": result['usage'],
            "raw_answer": str(result['answer'])
        }
    }
    time.sleep(1.0)

    if result.get("tie_breaker_used"):
         yield {
            "step": "AGGREGATION",
            "message": "Diverging answers detected. Calculating median...",
            "type": "alert"
        }
         time.sleep(1.0)

    # Final Result
    yield {
        "step": "COMPLETE",
        "message": "Workflow Complete",
        "timestamp": time.time(),
        "final_payload": {
            "question": question,
            "importance": importance,
            "budget": budget,
            "answer": result["answer"],
            "usage": result["usage"]
        }
    }
