'''
This module is responsible for consolidating the verbose knowledge log
into a high-level episodic memory summary.
'''

import os
import re

KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'KNOWLEDGE.md')
EPISODIC_MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'EPISODIC_MEMORY.md')

def summarize_knowledge_to_episodic_memory():
    """
    Reads the raw KNOWLEDGE.md, creates a summary, and appends it to EPISODIC_MEMORY.md.
    Then, it clears the raw knowledge file for the next run.
    """
    if not os.path.exists(KNOWLEDGE_FILE):
        print("INFO: No knowledge file to summarize.")
        return

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        print("INFO: Knowledge file is empty. No summary generated.")
        return

    # --- Basic Summary Generation Logic ---
    goal_match = re.search(r'goal: "(.*?)"\n', content)
    goal = goal_match.group(1) if goal_match else "Unknown Goal"

    entries = content.strip().split('---\n')
    task_count = len(entries)
    final_entry = entries[-1]
    status_match = re.search(r"- \*\*Status:\*\* `(.*)`", final_entry)
    final_status = status_match.group(1) if status_match else "Unknown"

    summary = f"""## Episode Summary

- **Goal:** {goal}
- **Outcome:** {final_status}
- **Total Steps:** {task_count}

### Narrative
"""

    if final_status == "Success":
        summary += "The agent successfully completed the goal by executing a series of tasks."
    else:
        error_match = re.search(r"- \*\*Stderr:\*\*\n```\n(.*?)\n```", final_entry, re.DOTALL)
        error_details = error_match.group(1).strip() if error_match else "No specific error message found."
        summary += f"The agent failed to complete the goal. The final error was: {error_details}"
    
    summary += "\n---\n"

    # Append to episodic memory
    with open(EPISODIC_MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(summary)

    # Clear the working memory (raw knowledge file)
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        f.write("")

    print(f"INFO: Episodic memory updated and working memory cleared.")

if __name__ == '__main__':
    summarize_knowledge_to_episodic_memory()
