# Portfolio Notes

Use these notes when presenting the project on GitHub, a resume, or in an interview.

## GitHub About

Policy-driven calendar scheduling PoC with configurable business rules, conflict detection, dry-run previews, diagnostics, and auditable execution traces.

## Suggested Topics

`python` `calendar` `scheduling` `workflow-automation` `business-rules` `dry-run` `diagnostics` `process-automation` `pytest` `pydantic`

## Resume Bullet Options

Technical:

> Built a Python scheduling orchestration proof of concept using configurable business rules, deterministic candidate generation, calendar conflict filtering, dry-run previews, structured diagnostics, JSON execution traces, and automated tests.

Business/process:

> Designed a scheduling workflow prototype that translates process requirements into configurable rules, checks calendar conflicts, and produces reviewable dry-run recommendations with auditable trace output.

Balanced internship-friendly:

> Built a policy-driven calendar scheduling proof of concept that separates scheduling policy, calendar access, decision logic, and execution flow for maintainability, testing, and clear business-process documentation.

## Interview Answer

"This project is a Python proof of concept for calendar scheduling orchestration. A scheduling request is passed to the CLI, and the system uses configured business rules to generate candidate slots, filter calendar conflicts, and recommend the earliest valid time. I used a deterministic mock calendar adapter so the workflow can be tested repeatably. The project also includes dry-run previews, diagnostics, JSON traces, and automated tests, which makes the decision process easier to inspect instead of hiding it in one black-box step."
