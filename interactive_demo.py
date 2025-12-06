import sys
from thinking_budget import run_single_question

def main():
    print("Welcome to the Thinking-Budget Controller Demo!")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            print("-" * 50)
            question = input("Enter your question: ").strip()
            if question.lower() in ('exit', 'quit'):
                break
            if not question:
                continue

            importance = input("Importance (low/normal/high) [normal]: ").strip().lower()
            if importance not in ('low', 'normal', 'high'):
                importance = "normal"

            print(f"\nProcessing with importance='{importance}'...\n")
            
            try:
                result = run_single_question(question, importance=importance)
                
                budget = result['budget']
                usage = result['usage']
                
                print(f"Decision:  {budget['budget_label'].upper()} (Effort: {budget['reasoning_effort']}, Paths: {budget['paths']})")
                print(f"Answer:    {result['answer']}")
                print(f"Usage:     {usage['total_tokens']} tokens (Reasoning: {usage['reasoning_tokens']})")
                
            except Exception as e:
                print(f"Error: {e}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
            
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
