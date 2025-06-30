# G.E.A.R. Agent Operating Protocol

## 1. Introduction

This document defines the Standard Operating Procedure (SOP) I must follow when receiving complex, long-term instructions that require local machine operations. The **G.E.A.R. (Goal-oriented Execution and Adaptive Response)** agent is not just a tool, but an extension of my own cognitive and execution loop. This protocol ensures that task execution is portable, consistent, goal-oriented, and self-correcting.

## 2. Core Principles

- **Portability:** The agent is designed to be portable. However, due to the `pywinauto` dependency, **GUI automation is currently Windows-only**.
- **Environment Safety:** The agent **MUST** operate exclusively within a `.venv` virtual environment, managed by `uv`, to prevent contamination of the global Python environment.
- **Resource Efficiency:** The agent will always prefer non-graphical interactions (CLI, API calls) over GUI automation. GUI operations will only be used when no other method is available to achieve the goal, thus conserving computational resources.
- **Goal-Oriented:** All actions are driven by a single, high-level goal defined in `goal.txt`.
- **Adaptive Execution:** The agent uses a reactive loop (Observe, Orient, Decide, Act). It does not follow a static plan but determines the next best action based on the outcome of the previous step.
- **Dual-Tier Memory:** The agent uses a two-tiered memory system to manage context length and enable learning:
    - **Working Memory (`assets/KNOWLEDGE.md`):** A verbose, short-term log of all actions taken within a single operational run. Used by the agent for tactical, step-by-step decisions.
    - **Episodic Memory (`assets/EPISODIC_MEMORY.md`):** A condensed, long-term summary of the outcomes of each goal-oriented run. This is used by me (the Gemini-CLI) for strategic analysis and reporting, keeping my context lean.

## 3. Execution Workflow

**Step 1: Goal Clarification & Registration**
1.  I will first engage in a dialogue with the user to clarify any ambiguity and distill their request into a clear, concise, and measurable **"Essential Goal."**
2.  I will write this Essential Goal into `goal.txt`. This is the official act of delegating the task to the G.E.A.R. agent.
    - **Tool:** `write_file`

**Step 2: Agent Invocation**
1.  I will activate the agent by executing its main loop within the mandatory virtual environment.
    - **Tool:** `run_shell_command`
    - **Command:** `.venv\Scripts\activate && python -m src.main`

**Step 3: Agent's Autonomous Loop**
1.  The agent starts and reads the goal from `goal.txt`.
2.  It enters the **Observe-Decide-Act-Record** loop:
    a. **Observe:** Reads the entire `assets/KNOWLEDGE.md` (Working Memory) to understand the current state.
    b. **Decide:** The `planner` module determines the single next best action based on the Essential Goal and the history.
    c. **Act:** The appropriate controller (`shell`, `gui`, `web`) executes the action.
    d. **Record:** The result (success/failure, stdout/stderr) is recorded verbosely in `assets/KNOWLEDGE.md`.
3.  This loop continues until the `planner` deems the goal complete or encounters a definitive failure.

**Step 4: Memory Consolidation**
1.  After the agent's run is complete, I will execute the memory summarizer script.
    - **Tool:** `run_shell_command`
    - **Command:** `.venv\Scripts\activate && python -m src.memory_summarizer`
2.  This script reads the verbose `KNOWLEDGE.md`, generates a high-level summary of the episode, appends it to `assets/EPISODIC_MEMORY.md`, and clears `KNOWLEDGE.md` for the next run.

**Step 5: Analysis, Reporting, and Cleanup**
1.  I will read the newly created summary in `assets/EPISODIC_MEMORY.md` to understand the outcome without consuming the entire raw log.
2.  I will report the outcome to the user, referencing the episodic summary.
3.  After receiving user confirmation, I will clear `goal.txt` to prepare the agent for its next mission.
    - **Tool:** `write_file` (with empty content)


