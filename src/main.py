"""
Main entry point for the G.E.A.R. agent.
Orchestrates the goal-oriented, reactive loop of the agent.
"""

import time
import os
import json

from src.task_executor import execute_shell_command
from src.knowledge_manager import record_knowledge, read_knowledge_history
from src.gui_controller import GUIController, WebController
from src.planner import determine_next_step

GOAL_FILE = "goal.txt"
MAX_LOOPS = 10 # Safety break to prevent infinite loops

def execute_task(task: str, gui_controller: GUIController, web_controller: WebController) -> tuple[bool, str, str, str]:
    """
    Executes a single task string.
    Returns a tuple of (success, command, stdout, stderr).
    """
    success, stdout, stderr = False, "", ""
    command = "n/a"

    try:
        if task.startswith('shell:'):
            command = task.split('shell:', 1)[1].strip()
            success, stdout, stderr = execute_shell_command(command)

        elif task.startswith('gui:'):
            parts = task.split(':', 2)
            action = parts[1].strip()
            params_str = parts[2].strip() if len(parts) > 2 else "{}"
            params = json.loads(params_str)
            command = f"gui:{action}"

            action_map = {
                'start': lambda: gui_controller.start_application(path=params.get("path"), title_re=params.get("title"), aumid=params.get("aumid")),
                'close': lambda: gui_controller.close_current_application(),
                'close_by_name': lambda: gui_controller.close_application_by_name(params.get("app_name")),
                'click': lambda: gui_controller.click_element(params.get("control_identifiers")),
                'type': lambda: gui_controller.type_text_in_element(params.get("control_identifiers"), params.get("text")),
                'keys': lambda: gui_controller.send_keys_to_app(params.get("keys")),
                'print_identifiers': lambda: (gui_controller.print_app_control_identifiers(), "Printed to console")[0],
            }
            if action in action_map:
                success = action_map[action]()
                stdout = f"GUI action '{action}' executed."
            else:
                stderr = f"Unsupported GUI action: {action}"

        elif task.startswith('web:'):
            parts = task.split(':', 2)
            action = parts[1].strip()
            params_str = parts[2].strip() if len(parts) > 2 else "{}"
            params = json.loads(params_str)
            command = f"web:{action}"

            action_map = {
                'launch': lambda: web_controller.launch_browser(browser_type=params.get("browser_type", "chromium"), headless=params.get("headless", True)),
                'navigate': lambda: web_controller.navigate(params.get("url")),
                'type': lambda: web_controller.type_text_web(params.get("selector"), params.get("text")),
                'click': lambda: web_controller.click_element_web(params.get("selector")),
                'wait': lambda: web_controller.wait_for_selector(
                    params.get("selector"),
                    state=params.get("state", "visible"),
                    timeout=params.get("timeout", 30000)
                ),
                'close': lambda: web_controller.close_browser(),
            }
            if action in action_map:
                success = action_map[action]()
                stdout = f"Web action '{action}' executed."
            else:
                stderr = f"Unsupported Web action: {action}"
        
        else:
            stderr = f"Unknown task type for task: {task}"

    except json.JSONDecodeError as e:
        stderr = f"Error parsing parameters for task '{task}': {e}"
    except Exception as e:
        stderr = f"An unexpected error occurred during execution of task '{task}': {e}"

    if not success and not stderr:
        stderr = f"Task '{command}' failed without explicit error."

    return success, command, stdout, stderr

# --- Path Setup ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GOAL_FILE = os.path.join(PROJECT_ROOT, "goal.txt")

def main_loop():
    """
    The main operational loop of the G.E.A.R. agent.
    """
    if not os.path.exists(GOAL_FILE) or os.path.getsize(GOAL_FILE) == 0:
        print("INFO: Goal file is empty or does not exist. Agent has nothing to do.")
        return

    with open(GOAL_FILE, "r", encoding="utf-8") as f:
        high_level_goal = f.read().strip()

    print(f"G.E.A.R. agent starting with goal: \"{high_level_goal}\"")

    gui_controller = GUIController()
    web_controller = WebController()
    
    loop_count = 0
    try:
        while loop_count < MAX_LOOPS:
            loop_count += 1
            print(f"\n--- Agent Loop {loop_count}/{MAX_LOOPS} ---")

            # 1. OBSERVE: Read the history of actions
            history = read_knowledge_history()

            # 2. ORIENT & DECIDE: Determine the next step
            next_task = determine_next_step(high_level_goal, history)

            if next_task is None:
                print("INFO: Goal achieved or no further steps can be determined. Shutting down.")
                break

            # 3. ACT: Execute the task
            print(f"--> Executing task: {next_task}")
            success, command, stdout, stderr = execute_task(next_task, gui_controller, web_controller)
            status = "Success" if success else "Failure"
            print(f"--> Task status: {status}")

            # 4. RECORD: Record the outcome
            learning = f"Executed task '{next_task}' as part of goal '{high_level_goal}'."
            record_knowledge(
                high_level_goal=high_level_goal,
                task=next_task,
                command=command,
                status=status,
                stdout=stdout,
                stderr=stderr,
                learning=learning
            )

            if not success:
                print(f"ERROR: Task failed. See assets/KNOWLEDGE.md for details. Stopping for safety.")
                break
            
            time.sleep(2) # Pause between steps

    except Exception as e:
        print(f"FATAL: An unexpected exception broke the main loop: {e}")
    finally:
        # Cleanup resources
        if web_controller.browser:
            web_controller.close_browser()
        print("\n--- G.E.A.R. agent shutdown complete. ---")


if __name__ == "__main__":
    main_loop()
