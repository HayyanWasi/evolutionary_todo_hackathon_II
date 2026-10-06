# Evolution of Todo — Phase I: console app

## What this is
In-memory Python console todo app. Phase I of a 5-phase project.
Tasks live in memory only and are lost on exit. This is on purpose.

Phase I requirements: specs/features/task-crud.md — read before changing code.

## Stack
- Python 3.13+, managed with uv
- Code in src/, tests in tests/

## Commands
- Run: <fill in once it exists>
- Test: uv run pytest
- Add a package: uv add <name>   (never pip install)

## Rules
- Phase I scope only: add, delete, update, view, mark complete.
  No priorities, due dates, tags, files, or database. Those are later phases.
- Ask me before adding any new dependency.
- Run the tests before saying a task is done.