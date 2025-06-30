# G.E.A.R. - Gemini-driven Execution, and Autonomic Refinement Agent

G.E.A.R. is an experimental agent designed to understand and execute tasks described in a simple text file. It leverages the Gemini CLI's problem-solving framework to perform a variety of operations, including shell commands and complex GUI automation on Windows.

## Core Concepts

- **Task-driven:** The agent operates based on a `ToDo.md` task list.
- **Multi-modal Execution:** It can execute shell commands, control desktop GUI applications, and automate web browsers.
- **Autonomous Operation:** It works autonomously through the task list until it's completed or an error occurs.
- **Knowledge Management:** It learns from its actions and records the outcomes in `docs/KNOWLEDGE.md` for analysis. This file is not committed to the repository.

## ⚠️ Security Warning

This agent uses `subprocess.run(shell=True)` to execute commands from `ToDo.md`. This provides great flexibility but also carries significant security risks. **Only run tasks from trusted sources.** Malicious commands in `ToDo.md` could harm your system.

## Setup

0.  **Install Gemini CLI**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kadubon/GEAR.git
    cd GEAR
    ```

2.  **Create a virtual environment and install dependencies:**
    This project uses `uv` for environment and package management.
    ```bash
    # Make sure `uv` is installed (e.g., `pip install uv`)
    uv venv
    # Activate the environment
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    # source .venv/bin/activate
    
    # Install dependencies
    uv pip install -r requirements.txt
    ```

## How to Use

1.  **Define your tasks in `ToDo.md`:**
    Populate the `ToDo.md` file with tasks for the agent to complete. Use the format `- [ ] Your task description`. The agent will execute the first unfinished task it finds.

2.  **Task Types:**
    G.E.A.R. identifies tasks by prefixes. Parameters are provided as a JSON string.

    *   **`shell:`**: Executes a shell command.
        - Example: `- [ ] shell: python --version`

    *   **`gui:`**: Performs desktop GUI automation. The agent manages one active application at a time.
        - **`start`**: Starts an application.
            - `path`: Path to a `.exe`.
            - `aumid`: AUMID for UWP apps.
            - `title`: Optional regex to identify the window title.
            - Example (Notepad): `- [ ] gui:start:{"path": "notepad.exe"}`
            - Example (UWP): `- [ ] gui:start:{"aumid": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App", "title": "Calculator"}`
        - **`click`**: Clicks a UI element in the active application.
            - `control_identifiers`: A dictionary of `pywinauto` identifiers.
            - Example: `- [ ] gui:click:{"control_identifiers": {"title": "1", "control_type": "Button"}}`
        - **`type`**: Types text into a UI element.
            - `control_identifiers`: Identifiers for the target element.
            - `text`: The text to type.
            - Example: `- [ ] gui:type:{"control_identifiers": {"control_type": "Edit"}, "text": "Hello from G.E.A.R.!"}`
        - **`keys`**: Sends keyboard shortcuts/keys to the active application.
            - `keys`: The key sequence (e.g., `^s` for Ctrl+S).
            - Example: `- [ ] gui:keys:{"keys": "^s"}`
        - **`print_identifiers`**: Prints all control identifiers for the active app's main window to the console. Useful for debugging.
            - Example: `- [ ] gui:print_identifiers:{}`
        - **`list_windows`**: Lists all currently open windows with their title, class, and PID.
            - Example: `- [ ] gui:list_windows:{}`
        - **`close`**: Closes the currently active application.
            - Example: `- [ ] gui:close:{}`
        - **`close_by_name`**: Closes an application by its executable name.
            - `app_name`: The process name (e.g., `notepad.exe`).
            - Example: `- [ ] gui:close_by_name:{"app_name": "notepad.exe"}`

3.  **Run the agent:**
    Ensure your virtual environment is activated.
    ```bash
    python -m src.main
    ```

4.  **Monitor progress:**
    - The agent's progress can be tracked by observing `ToDo.md` as tasks are marked `[x]`.
    - Detailed logs and outcomes are recorded in `docs/KNOWLEDGE.md`.

## Running Tests

To ensure the integrity of the agent's components, run the unit tests:
```bash
python -m unittest discover tests
