import os
import sys

def check_venv():
    """
    Checks if the script is running inside a virtual environment.
    """
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("Error: This script is not running in a virtual environment.")
        print("Please activate your virtual environment before running.")
        sys.exit(1)
    else:
        print("Running in a virtual environment.")

if __name__ == "__main__":
    check_venv()
