# Threat Model

This is a lightweight threat model for the current proof of concept and possible future calendar adapters.

## Current Scope

The current implementation uses a deterministic mock calendar adapter. It does not connect to a real calendar account, store real user credentials, or send data to an external service.

## Data Handled Today

- scheduling goal text passed to the CLI
- generated candidate slots
- mock busy blocks
- event body preview
- diagnostics and timing metrics
- JSON trace files written to `runs/`

## Privacy Considerations

The engine parses busy time ranges and does not need event titles to make conflict decisions. This is a useful pattern for a future real-calendar adapter because scheduling logic can often work with free/busy blocks instead of sensitive event details.

## Dry-Run Safety

Dry-run mode previews the selected slot and event body without creating an event. This makes the workflow easier to review before any calendar action is taken.

## Future Integration Risks

If a live calendar adapter is added later, the main risks will be:

- protecting OAuth credentials and tokens
- avoiding unnecessary storage of event titles or descriptions
- making event creation opt-in and reviewable
- handling API errors and rate limits clearly
- preventing future request parsing from overriding explicit policy rules

## Mitigations Already Reflected in the Design

- policy is separated from execution
- dry-run mode is supported
- diagnostics explain workflow steps
- tests cover deterministic scheduling behavior
- mock adapter enables repeatable local testing
