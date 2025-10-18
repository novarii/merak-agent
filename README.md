## Merak Trip Planner Agent

This repo now includes a minimal example of building a travel-planning agent using the [OpenAI Agents Python SDK](https://openai.github.io/openai-agents-python/).

### Prerequisites
- Python 3.11
- An OpenAI API key (`OPENAI_API_KEY`)

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the Trip Planner
By default the CLI starts an interactive REPL that keeps the conversation history for the duration of the process. You can optionally seed the first turn via CLI arguments.

```bash
export OPENAI_API_KEY=sk-...
python3 scripts/run_trip_planner.py
# or seed the opening request
python3 scripts/run_trip_planner.py "Plan a spring honeymoon in Japan focused on culture and food."
```

Type `exit` or `quit` to end the chat. Supply `--session-id my_trip` to persist the thread with `SQLiteSession` and resume it later.

### Single-Turn Mode
Use the `--single-turn` flag when you only need a one-off itinerary.

```bash
export OPENAI_API_KEY=sk-...
python3 scripts/run_trip_planner.py --single-turn "Plan a winter ski escape in the Alps."
```

### Tests
```bash
pytest
```
