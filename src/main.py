"""
Main entry point for the G.E.A.R. agent.
Orchestrates parsing tasks, executing them, and recording knowledge.
"""

import time
import os
import json

from src.task_parser import find_next_task
from src.task_executor import execute_shell_command
from src.knowledge_manager import record_knowledge
from src.gui_controller import GUIController, WebController

TODO_FILE = "ToDo.md"

def main_loop():
    """
    The main operational loop of the G.E.A.R. agent.
    """
    gui_controller = GUIController()
    web_controller = WebController()

    while True:
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            
            next_task = find_next_task(content)
            
            if next_task is None:
                print("All tasks completed. Shutting down.")
                break

            print(f"--> Executing task: {next_task}")

            if next_task.startswith('shell:'):
                command_to_run = next_task.split('shell:', 1)[1].strip()
                success, stdout, stderr = execute_shell_command(command_to_run)
                status = "Success" if success else "Failure"
                learning = "Executed a direct shell command."
                record_knowledge(
                    task=next_task,
                    command=command_to_run,
                    status=status,
                    stdout=stdout,
                    stderr=stderr,
                    learning=learning
                )
            elif next_task.startswith('gui:'):
                gui_command_parts = next_task.split(':', 2)
                gui_action = gui_command_parts[1].strip()
                gui_params_json_str = gui_command_parts[2].strip() if len(gui_command_parts) > 2 else "{}"

                print(f"    > GUI Task: {gui_action} with parameters: {gui_params_json_str}")

                try:
                    params = json.loads(gui_params_json_str)
                    success = False
                    stdout = ""
                    stderr = ""
                    learning = ""

                    if gui_action == 'start':
                        success = gui_controller.start_application(
                            path=params.get("path"),
                            title_re=params.get("title"),
                            aumid=params.get("aumid")
                        )
                        stdout = "Application started successfully." if success else "Failed to start application."
                        learning = f"Attempted to start application."
                    elif gui_action == 'close':
                        success = gui_controller.close_current_application()
                        stdout = "Application closed successfully." if success else "Failed to close application."
                        learning = "Attempted to close application."
                    elif gui_action == 'close_by_name':
                        success = gui_controller.close_application_by_name(params.get("app_name"))
                        stdout = "Application closed successfully." if success else "Failed to close application."
                        learning = f"Attempted to close application by name: {params.get('app_name')}"
                    elif gui_action == 'click':
                        success = gui_controller.click_element(params.get("control_identifiers"))
                        stdout = "Clicked successfully." if success else "Element not found or click failed."
                        learning = f"Attempted to click GUI element."
                    elif gui_action == 'type':
                        success = gui_controller.type_text_in_element(params.get("control_identifiers"), params.get("text"))
                        stdout = "Text typed successfully." if success else "Failed to type text."
                        learning = f"Attempted to type text in GUI element."
                    elif gui_action == 'keys':
                        success = gui_controller.send_keys_to_app(params.get("keys"))
                        stdout = "Keys sent successfully." if success else "Failed to send keys."
                        learning = f"Attempted to send keys."
                    elif gui_action == 'print_identifiers':
                        gui_controller.print_app_control_identifiers()
                        success, stdout = True, "Control identifiers printed to console."
                        learning = f"Printed control identifiers."
                    else:
                        stderr = f"Unsupported GUI action or missing parameters: {gui_action}"
                    
                    status = "Success" if success else "Failure"
                    if not success and not stderr:
                        stderr = stdout
                    
                    record_knowledge(
                        task=next_task,
                        command=f"gui:{gui_action}",
                        status=status,
                        stdout=stdout,
                        stderr=stderr,
                        learning=learning
                    )

                except json.JSONDecodeError as e:
                    status = "Failure"
                    stderr = f"Error parsing GUI parameters (JSON): {e}"
                    record_knowledge(task=next_task, command=f"gui:{gui_action}", status=status, stdout="", stderr=stderr, learning=f"Failed to parse GUI parameters. Error: {e}")

            else:
                status = "RequiresPlanning"
                learning = f"The task '{next_task}' is a high-level goal that needs to be broken down into executable steps."
                record_knowledge(task=next_task, command="N/A", status=status, stdout="", stderr="", learning=learning)


            print(f"--> Task status: {status}")

            if status == "Success":
                new_content = content.replace(f"- [ ] {next_task}", f"- [x] {next_task}", 1)
                with open(TODO_FILE, "w", encoding="utf-8") as f:
                    f.write(new_content)
            elif status == "RequiresPlanning":
                print("Task requires planning. Please refine the ToDo.md.")
                break
            else:
                print(f"Task failed. See docs/KNOWLEDGE.md. Stopping for safety.")
                break

        except FileNotFoundError:
            print(f"Error: {TODO_FILE} not found. Please create it.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

        time.sleep(2)

if __name__ == "__main__":
    print("G.E.A.R. agent starting...")
    main_loop()
