# Policy-Driven AI Orchestration — Google Calendar Integration

This repository contains a policy-first AI orchestration system designed to make
AI-assisted workflows reliable in real-world environments.

The system integrates with Google Calendar via OAuth, enforces explicit scheduling
policies, and produces auditable run traces. It includes self-diagnostics, a
simulation mode, and regression tests to validate deterministic behavior.

---

## What it does

Given a goal such as:

> “Schedule a 30-minute interview prep block this week”

The orchestration pipeline:

1. Reads busy time blocks from a partner calendar API
2. Generates candidate time slots based on explicit policy constraints
3. Filters conflicts deterministically
4. Selects the earliest valid slot and records *why*
5. Supports dry-run previews or real execution
6. Writes an auditable run trace to `runs/`

---

## Why this exists

AI systems often fail not because models are weak, but because orchestration,
integration, and observability break down in real environments.

This project is designed the way production systems are:
- policy separated from execution
- deterministic by default
- safe dry-run gates
- self-diagnostics before execution
- regression-tested behavior

---

## Quick start (simulation — no credentials required)

```bash
python -m src.app simulate --dry-run
