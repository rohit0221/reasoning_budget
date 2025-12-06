import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def load_questions(file_path: str) -> List[Dict[str, Any]]:
    """Loads questions from a JSONL file."""
    questions = []
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at {file_path}")
        
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions
