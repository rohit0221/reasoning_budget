import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict
from collections import defaultdict
import statistics

from .dataset import load_questions
from .controller import BudgetController
from .agent import ReasoningAgent
from .config import BUDGET_PROFILES
from .logging_utils import append_log

# Load env vars
load_dotenv()

def calculate_accuracy(pred: float, truth: float, tolerance: float = 0.1) -> bool:
    if pred is None:
        return False
    return abs(pred - truth) < tolerance

def run_evaluation():
    parser = argparse.ArgumentParser(description="Run Thinking-Budget POC Evaluation")
    parser.add_argument("--questions", default="data/questions.jsonl", help="Path to questions file")
    parser.add_argument("--logs", default="data/runs.jsonl", help="Path to output logs")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env")
        return

    client = OpenAI(api_key=api_key)
    
    controller = BudgetController(client)
    agent = ReasoningAgent(client)
    
    questions = load_questions(args.questions)
    print(f"Loaded {len(questions)} questions.")

    strategies = ["always_fast", "always_deep", "adaptive"]
    
    # Metrics storage
    metrics = {s: defaultdict(int) for s in strategies}
    # For averages
    raw_stats = {s: {"output_tokens": [], "reasoning_tokens": []} for s in strategies}

    for i, q_item in enumerate(questions):
        print(f"Processing Q{i+1}: {q_item['id']}...")
        
        for strategy in strategies:
            # Determine Budget
            if strategy == "always_fast":
                budget_decision = {
                    "budget_label": "fast",
                    **BUDGET_PROFILES["fast"],
                    "difficulty": "N/A" # Not calculated
                }
            elif strategy == "always_deep":
                budget_decision = {
                    "budget_label": "deep",
                    **BUDGET_PROFILES["deep"],
                    "difficulty": "N/A"
                }
            else: # adaptive
                budget_decision = controller.decide_budget(q_item["question"], q_item.get("importance", "normal"))

            # Run Agent
            result = agent.solve(q_item["question"], budget_decision)
            
            # Evaluate
            is_correct = calculate_accuracy(result["answer"], q_item["answer"])
            
            # Update Metrics
            metrics[strategy]["total"] += 1
            if is_correct:
                metrics[strategy]["correct"] += 1
            metrics[strategy]["total_tokens"] += result["usage"]["total_tokens"]
            metrics[strategy]["total_reasoning_tokens"] += result["usage"]["reasoning_tokens"]
            
            raw_stats[strategy]["output_tokens"].append(result["usage"]["completion_tokens"])
            raw_stats[strategy]["reasoning_tokens"].append(result["usage"]["reasoning_tokens"])

            # Log
            log_entry = {
                "run_id": f"{strategy}_{q_item['id']}",
                "strategy": strategy,
                "question_id": q_item["id"],
                "question": q_item["question"],
                # "importance": q_item.get("importance", "normal"), # Added to q_item in dataset
                **q_item, # includes importance, answer etc
                "budget_label": budget_decision["budget_label"],
                "reasoning_effort": budget_decision["reasoning_effort"],
                "paths": budget_decision["paths"],
                "difficulty_est": budget_decision.get("difficulty"),
                "predicted_answer": result["answer"],
                "correct": is_correct,
                "usage": result["usage"],
                "raw_outputs": result["raw_outputs"]
            }
            append_log(args.logs, log_entry)

    # Print Summary Table
    print("\n" + "="*80)
    print(f"{'Strategy':<15} {'Acc':<10} {'AvgOutTok':<12} {'AvgReasTok':<12} {'TotalTok':<12}")
    print("-" * 80)
    
    for strategy in strategies:
        total = metrics[strategy]["total"]
        if total == 0:
            continue
        acc = metrics[strategy]["correct"] / total
        avg_out = statistics.mean(raw_stats[strategy]["output_tokens"]) if raw_stats[strategy]["output_tokens"] else 0
        avg_reas = statistics.mean(raw_stats[strategy]["reasoning_tokens"]) if raw_stats[strategy]["reasoning_tokens"] else 0
        total_tok = metrics[strategy]["total_tokens"]
        
        print(f"{strategy:<15} {acc:<10.2f} {avg_out:<12.1f} {avg_reas:<12.1f} {total_tok:<12}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_evaluation()
