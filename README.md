# agentic-data-analysis

Autonomous data analysis loop using Gemini and Pandas

An autonomous agent that accepts high-level natural language data analysis requests, generates Pandas code using Google Gemini, executes the code safely in-memory, and self-corrects if execution fails.

## Features

- **Natural Language Data Queries**: Ask whatever you'd like about your CSV files in plain English.
- **In-Memory Code Execution**: Automatically builds and executes Python Pandas queries against loaded DataFrames.
- **Self-Correction Loop**: Catches Python runtime errors and feeds tracebacks back to Gemini to auto-fix buggy code (up to 3 iterations).
- **Interactive Shell**: Interactive terminal UI with built-in metadata commands (`info`, `history`, `quit`).

## Installation

1. Clone the repository:

```bash
git clone https://github.com/austinfutures/agentic-data-analysis.git
cd agentic-data-analysis
```

2. Install dependencies:

```bash
pip install google-genai pandas numpy
```

3. Set your Google Gemini API Key:

**Windows (Command Prompt):**

```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
```

**Linux / macOS / PowerShell:**

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

## Quickstart

Save your target data as `data.csv` in the root directory, then start an interactive session:

```python
from agent import DataAnalysisAgent

# Initialize agent
agent = DataAnalysisAgent(model="gemini-3.5-flash")

# Load data
agent.load_data("data.csv")

# Start interactive shell
agent.interactive_session()
```

### Direct Programmatic Queries

```python
from agent import DataAnalysisAgent

agent = DataAnalysisAgent(model="gemini-3.5-flash")
agent.load_data("sales.csv")
agent.execute_query("What are the top 5 revenue generating product categories?")
```

## Commands in Interactive Mode

| Command | Action |
|---------|--------|
| `info` | Displays DataFrame structure, types, and column counts |
| `history` | Prints JSON dump of code executed and error logs |
| `quit` | Exit the interactive session |

## Technical Details

- **SDK Used**: Google GenAI Python SDK (`google-genai`)
- **Execution Sandbox**: Executed via standard Python `exec()` against isolated local scope namespaces (`df`, `pd`, `np`)
- **Default Model**: `gemini-3.5-flash` (can be overridden during instantiation with any valid Gemini model identifier, e.g., `gemini-3.1-flash-lite`)
