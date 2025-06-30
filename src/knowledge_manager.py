"""
This module manages the agent's knowledge base (working memory).
"""

import datetime
import uuid
import os
import re

# --- Path Setup ---
# Dynamically determine the project root and assets directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')
KNOWLEDGE_FILE = os.path.join(ASSETS_DIR, "KNOWLEDGE.md")

def record_knowledge(
    high_level_goal: str,
    task: str,
    command: str,
    status: str,
    stdout: str,
    stderr: str,
    learning: str = "N/A"
) -> None:
    """
    Records the outcome of a task into the KNOWLEDGE.md file.
    """
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    # Compact knowledge entry format
    knowledge_entry = f"""---
id: {uuid.uuid4()}
timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
goal: "{high_level_goal}"
task: `{task}`
command: `{command}`
status: `{status}`
---
- **Stdout:**
```
{stdout.strip()}
```
- **Stderr:**
```
{stderr.strip()}
```
- **Learning:** {learning}
---

"""
    
    try:
        with open(KNOWLEDGE_FILE, "a", encoding="utf-8") as f:
            f.write(knowledge_entry)
    except IOError as e:
        print(f"Error writing to knowledge base: {e}")

def read_knowledge_history() -> list[dict]:
    """
    Reads and parses the KNOWLEDGE.md file into a list of structured history entries.
    """
    history = []
    if not os.path.exists(KNOWLEDGE_FILE):
        return history

    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except IOError as e:
        print(f"Error reading knowledge base: {e}")
        return history

    entries = content.strip().split('---\n')
    
    for entry_text in entries:
        if not entry_text.strip():
            continue
        
        entry_data = {}
        try:
            # Use regex to parse the structured parts
            for line in entry_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    entry_data[key.strip()] = value.strip().replace('`','')
            
            history.append(entry_data)
        except Exception as e:
            print(f"Warning: Could not parse a knowledge entry. Error: {e}")
            continue
            
    return history
