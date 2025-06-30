"""
This module is responsible for executing shell commands.
"""

import subprocess

def execute_shell_command(command: str) -> tuple[bool, str, str]:
    """
    Executes a shell command and captures its output.

    Args:
        command: The shell command to execute.

    Returns:
        A tuple containing:
        - bool: True if the command was successful (exit code 0), False otherwise.
        - str: The standard output of the command.
        - str: The standard error of the command.
    """
    try:
        process = subprocess.run(
            command, 
            shell=True, 
            check=False, 
            capture_output=True, 
            text=True
        )
        success = process.returncode == 0
        return success, process.stdout, process.stderr
    except Exception as e:
        return False, "", str(e)
