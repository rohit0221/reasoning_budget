from thinking_budget.demo import run_single_question
import json

print("Running single question demo...")
try:
    result = run_single_question(
        "A product is 1000, 20% discount then 18% tax. Final price?",
        importance="high",
    )
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"FAILED: {e}")
