import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

def append_log(file_path: str, data: Dict[str, Any]):
    """Appends a log entry to a JSONL file."""
    # Ensure directory exists
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
