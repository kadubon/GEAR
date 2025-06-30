# G.E.A.R. - Goal-oriented Execution and Adaptive Response Agent

## 1. Overview

G.E.A.R. is a sophisticated, autonomous agent designed to understand and execute complex, long-term tasks on a local machine. It bridges the gap between high-level user goals and the low-level actions (shell commands, GUI interactions, web browsing) required to achieve them.

This system is intended to be operated by a controlling entity (like the Gemini-CLI) that defines a goal. The agent then takes over, pursuing the goal with a persistent, self-correcting, and adaptive loop.

## 2. Core Principles

- **Portability:** The agent is designed to be fully portable. It uses dynamic path resolution and is not tied to any specific machine's file structure.
- **Environment Safety:** G.E.A.R. **must** operate within a Python virtual environment (`.venv`) to ensure all dependencies are isolated and the host system's global environment is not affected.
- **Goal-Oriented:** The agent's entire operation is driven by a single, clearly defined goal specified in `goal.txt`.
- **Adaptive Execution:** It employs a reactive **Observe-Decide-Act-Record** loop. Instead of following a rigid, pre-defined plan, it determines the next best action based on the real-time outcome of its previous step.
- **Dual-Tier Memory:** To enable learning without context overload, the agent uses two forms of memory:
    - **Working Memory (`assets/KNOWLEDGE.md`):** A temporary, verbose log of every action taken to achieve a single goal.
    - **Episodic Memory (`assets/EPISODIC_MEMORY.md`):** A permanent, high-level summary of the outcome of each goal. This serves as the agent's long-term memory for strategic learning.

## 3. How to Use

Using the G.E.A.R. agent involves a simple, three-step process managed by its controlling entity.

### Step 1: Setup (First-Time Use)

Ensure you have Python and `uv` installed. Then, create and populate the virtual environment:

```bash
# Create the virtual environment
uv venv

# Activate the environment and install dependencies
.venv\Scripts\activate

uv pip install -r requirements.txt
```

### Step 2: Define a Goal

Manually or programmatically, write a clear, high-level objective into the `goal.txt` file. For example:

```
Search for today's weather in New York City and save it to a file.
```

### Step 3: Run the Agent

Activate the virtual environment and execute the main module. The agent will read the goal and begin its autonomous operation.

```bash
.venv\Scripts\activate && python -m src.main
```

The agent will run until the goal is completed or it determines it cannot proceed. All actions will be logged in `assets/KNOWLEDGE.md`.

### Step 4: Consolidate Memory (Optional but Recommended)

After a run, to save the learnings and clean up the working memory, run the memory summarizer:

```bash
.venv\Scripts\activate && python -m src.memory_summarizer
```

This will create a permanent, high-level record in `assets/EPISODIC_MEMORY.md` and prepare the agent for its next task.

## 4. Project Structure

```
GEAR/
├── .venv/                # Isolated Python virtual environment
├── assets/
│   ├── KNOWLEDGE.md      # (Working Memory) Verbose log of the current run
│   └── EPISODIC_MEMORY.md# (Long-Term Memory) Summaries of past runs
├── src/
│   ├── main.py           # Main execution loop of the agent
│   ├── planner.py        # Decides the next best action
│   ├── knowledge_manager.py # Manages reading/writing to memory files
│   ├── task_executor.py  # Executes shell commands
│   ├── gui_controller.py   # Handles GUI automation
│   └── memory_summarizer.py # Consolidates working memory into episodic memory
├── .gitignore
├── GEMINI.md             # The official operating protocol for the Gemini-CLI
├── goal.txt              # The input file for the agent's high-level goal
├── LICENSE
├── README.md             # This file
└── requirements.txt      # Python dependencies
```