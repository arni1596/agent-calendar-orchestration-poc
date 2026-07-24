# Failure Playbook

This file lists common issues and what to check first.

## No Slots Found

Possible causes:

- scheduling window is too narrow
- work hours are too restrictive
- minimum notice period pushes all candidates out of range
- event duration is too long
- mock busy blocks conflict with the available candidates

What to try:

- increase `WINDOW_END_DAYS`
- reduce `MIN_NOTICE_HOURS`
- reduce `DEFAULT_EVENT_DURATION_MIN`
- widen `WORK_START_HOUR` / `WORK_END_HOUR`

## Invalid Timezone

The engine validates `TIMEZONE` using `python-dateutil`. If the timezone is invalid, use an IANA timezone such as:

```text
America/Chicago
America/New_York
America/Los_Angeles
UTC
```

## Regression Test Cannot Find a Trace

`tests/test_regression.py` reads the latest `runs/sim_*.json` file. Run a simulation first:

```bash
python -m src.app simulate --dry-run
```

Then rerun:

```bash
python -m pytest
```

## Live Calendar Adapter Does Not Work

The current repository uses `MockCalendarClient` for deterministic simulation. `src/tools/google_calendar.py` is currently empty, so a live calendar account adapter is not implemented yet.

## Garbled Output or Documentation Characters

Use plain ASCII in comments and documentation. This keeps terminal output and GitHub rendering predictable across environments.
