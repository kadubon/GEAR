"""
This module is responsible for parsing the ToDo.md file
and extracting tasks.
"""

import re

def find_next_task(todo_content: str) -> str | None:
    """
    Finds the first unfinished task (line starting with '[ ]') in the ToDo.md content.

    Args:
        todo_content: The string content of the ToDo.md file.

    Returns:
        The text of the first unfinished task, or None if no unfinished tasks are found.
    """
    # Regex to find a line that starts with optional whitespace, then '[ ]', and captures the rest of the line.
    task_pattern = re.compile(r"^\s*\- \[ \] (.*)", re.MULTILINE)
    match = task_pattern.search(todo_content)
    
    if match:
        return match.group(1).strip()
    
    return None
