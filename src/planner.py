
"""
This module is responsible for determining the next best step for the agent
based on the high-level goal and the history of previous actions.
"""

import re

def determine_next_step(high_level_goal: str, history: list[dict]) -> str | None:
    """
    Determines the next single task to execute based on the goal and history.

    This is a state-machine-like planner. It checks the last successful action
    and decides the next logical step.

    Args:
        high_level_goal: The user's overall goal.
        history: A list of dictionaries, each representing a past action.

    Returns:
        A string representing the next task, or None if the goal is considered complete.
    """
    print(f"INFO: Determining next step for goal: '{high_level_goal}'")
    
    last_successful_task = None
    for event in reversed(history):
        if event.get('status') == 'Success':
            last_successful_task = event.get('task')
            break
    
    print(f"DEBUG: Last successful task was: '{last_successful_task}'")

    # Simple hard-coded logic for searching Google
    if "google" in high_level_goal.lower() and "search" in high_level_goal.lower():
        query_match = re.search(r"search for (.*)", high_level_goal, re.IGNORECASE)
        query = query_match.group(1).strip() if query_match else "large language models"

        if last_successful_task is None:
            return 'web: launch: {"headless": false}'
        
        if last_successful_task == 'web: launch: {"headless": false}':
            return f'web: navigate: {{"url": "https://www.google.com"}}'
            
        if last_successful_task.startswith('web: navigate:'):
            return f'web: type: {{"selector": "textarea[name=q]", "text": "{query}"}}'

        if last_successful_task.startswith('web: type:'):
            # This is a non-idempotent action, so we need to be careful.
            # A better check would be to see if the search results are visible.
            # For now, we assume the next step is to click.
            return f'web: click: {{"selector": "input[name=btnK]"}}'
        
        if last_successful_task.startswith('web: click:'):
            # After clicking search, the main part of this simple goal is done.
            print("INFO: Planner concludes the goal is complete.")
            return None # Returning None signifies completion

    # Default case if no plan is found
    print(f"WARNING: Planner has no next step for goal '{high_level_goal}' with last task '{last_successful_task}'.")
    return None # No further actions can be determined

