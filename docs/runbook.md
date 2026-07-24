# Runbook

Use this runbook to install the project, run the simulation, inspect outputs, and run tests.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Run a Dry-Run Simulation

```bash
python -m src.app simulate --dry-run
```

With a custom goal:

```bash
python -m src.app simulate --dry-run --goal "Schedule a 30-minute interview preparation block this week."
```

The simulation uses the deterministic mock calendar adapter and writes a trace file to `runs/`.

## Inspect the Trace

After running the simulation, open the newest file matching:

```text
runs/sim_*.json
```

Useful sections:

- `decision_explanation`: policy, selection rule, chosen-slot reason, and rejected summaries
- `result`: dry-run preview, chosen slot, alternatives, and event body preview
- `diagnostics`: structured workflow events
- `metrics`: basic timing measurements

## Run Tests

```bash
python -m pytest
```

`tests/test_regression.py` expects a generated simulation trace. If it fails because `runs/` is missing, run the dry-run simulation first and then rerun the tests.

## Configuration

Default scheduling settings live in `src/config.py` and can be overridden through environment variables or a local `.env` file. See `.env.example` for available values.
