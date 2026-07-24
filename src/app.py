from __future__ import annotations

import argparse

import structlog
from rich import print

from .simulate import run_simulation


def _configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )


def main() -> None:
    _configure_logging()

    parser = argparse.ArgumentParser(prog="agent-calendar-orchestration-poc")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sim_p = sub.add_parser(
        "simulate",
        help="Run orchestration against a deterministic mock calendar adapter (no credentials)",
    )
    sim_p.add_argument("--dry-run", action="store_true", help="Preview decisions without creating an event")
    sim_p.add_argument(
        "--goal",
        type=str,
        default="Schedule a 30-minute interview prep block this week.",
        help="Goal/intention used in event description",
    )

    args = parser.parse_args()

    if args.cmd == "simulate":
        trace = run_simulation(goal=args.goal, dry_run=True if args.dry_run else False)
        print("[bold green]Simulation complete[/bold green]")
        print(f"Status: {trace['result']['status']}")
        print("Simulation trace saved to runs/<request_id>.json")
        print("Metrics:")
        print(trace["metrics"])
        return


if __name__ == "__main__":
    main()
