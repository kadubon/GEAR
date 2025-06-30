"""
This module manages the agent's knowledge base,
writing structured summaries of actions to KNOWLEDGE.md.
"""

import datetime
import uuid

def record_knowledge(
    task: str,
    command: str,
    status: str,
    stdout: str,
    stderr: str,
    learning: str = "N/A"
) -> None:
    """
    Records the outcome of a task into the KNOWLEDGE.md file.

    Args:
        task: The high-level task description.
        command: The actual command executed.
        status: The execution status ('Success', 'Failure').
        stdout: The standard output from the command.
        stderr: The standard error from the command.
        learning: A summary of what was learned from this action.
    """
    knowledge_entry = f"""---
    id: {uuid.uuid4()}
    type: TaskExecution
    timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
    ---
    ### Summary
    Executed task: '{task}'

    ### Task
    - **Command:** `{command}`
    - **Status:** `{status}`
    - **Stdout:**
    ```
    {stdout.strip()}
    ```
    - **Stderr:**
    ```
    {stderr.strip()}
    ```

    ### Context & Learning
    {learning}

    ### Related Entities
    - `src/task_executor.py`
    - `docs/KNOWLEDGE.md`
    ---

    """
    
    try:
        with open("docs/KNOWLEDGE.md", "a", encoding="utf-8") as f:
            f.write(knowledge_entry)
    except IOError as e:
        print(f"Error writing to knowledge base: {e}")
