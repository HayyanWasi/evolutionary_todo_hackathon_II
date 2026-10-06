# Feature: Task CRUD (Phase I, in-memory console app)

Status: Step 1 (store layer) done, 26 tests passing, waiting for review. Step 2 (CLI) not started.

## Goal
A command-line todo app that keeps tasks in memory for one session. It covers the 5 Basic Level
features: Add, Delete, Update, View, Mark Complete. Tasks are lost on exit, and that is
intentional.

## User stories
1. As a user, I can add a task with a title and an optional description.
2. As a user, I can list all tasks and see whether each one is complete.
3. As a user, I can update a task's title and/or description.
4. As a user, I can delete a task by its ID.
5. As a user, I can mark a task complete, or mark it incomplete again.

## Acceptance criteria

### Task data
| Field | Type | Rule |
|---|---|---|
| `id` | int | Assigned by the app. Starts at 1, increases by 1, **never reused** after a delete. |
| `title` | str | Required. Surrounding whitespace is stripped. 1–200 characters after stripping. |
| `description` | str | Optional (defaults to `""`). Surrounding whitespace is stripped. At most 1000 characters. |
| `completed` | bool | `False` on creation. |

### Add
- A valid title (and optional description) creates a task with the next ID.
- An empty or whitespace-only title is rejected. So is a title over 200 characters or a
  description over 1000 characters. Nothing is created.

### View
- Tasks are listed in creation order.
- Each row shows ID, status (`[ ]` pending, `[x]` completed), title and description.
- A summary line follows: `N tasks, M completed`.
- An empty list shows `No tasks yet.`

### Update
- The title and/or description can be changed. A field that isn't given stays unchanged.
- Updates use the same validation as Add.
- **A failed update changes nothing.** Both fields are validated before either one is applied.
- Updating an unknown ID is an error.

### Delete
- Removes the task with that ID and reports its title.
- Deleting an unknown ID is an error.
- The deleted ID is not given to any later task.

### Mark complete / incomplete
- `done <id>` sets `completed = True`. `undo <id>` sets `completed = False`.
- Both are idempotent: marking an already-completed task complete is not an error.
- An unknown ID is an error.

### Errors (CLI)
- No error crashes the app. Each one prints one line and returns to the prompt.
- Unknown command: `Unknown command 'x'. Type 'help'.`
- Missing or non-numeric ID: `Usage: <command> <id>`
- Unknown ID: `Task #9 not found.`
- Invalid title or description: the validation message.

## Commands (interactive REPL, prompt `todo> `)
Commands are case-insensitive, and extra whitespace is ignored.

| Command | Behavior |
|---|---|
| `add` | Prompts `Title:` and `Description (optional):`, then prints `Added task #N.` |
| `list` | Prints the task table and the summary line, or `No tasks yet.` |
| `update <id>` | Shows the current values, then prompts for a new title and description. **Blank input keeps the current value.** |
| `delete <id>` | Prints `Deleted task #N: <title>.` |
| `done <id>` | Marks the task complete. |
| `undo <id>` | Marks the task incomplete. |
| `help` | Shows the command list. It is also shown once at startup. |
| `quit` / `exit` | Exits. EOF (Ctrl-D / Ctrl-Z) and Ctrl-C also exit cleanly. |

In the table, descriptions longer than about 40 characters are cut and end with `...`.

## Design
The code uses only the standard library. Package `todo` lives in `src/todo/`, and the entry point
is `todo = "todo.cli:main"`.

| Module | Responsibility |
|---|---|
| `models.py` | `Task` dataclass: `id`, `title`, `description=""`, `completed=False`. |
| `store.py` | `TaskStore`: in-memory CRUD, ID assignment, validation. No I/O. |
| `cli.py` | REPL: reads commands, prompts for fields, renders output. Talks only to `TaskStore`. |

`TaskStore` public API:
```python
add(title: str, description: str = "") -> Task
list_tasks() -> list[Task]                     # creation order
get(task_id: int) -> Task
update(task_id: int, title: str | None = None, description: str | None = None) -> Task
delete(task_id: int) -> Task                    # returns the removed task
set_completed(task_id: int, completed: bool) -> Task
```
Errors:
- `InvalidTaskError(ValueError)`: bad title or description.
- `TaskNotFoundError(LookupError)`: unknown ID.

`cli.run(store, read=input, write=print)` holds the loop. `read`/`write` are injected so tests can
script a session. `cli.main()` calls `run(TaskStore())`.

## Build order
Each step ends with `uv run pytest`. Then **stop and show the results for review** before
starting the next step.

1. **Store layer:** `models.py`, `store.py`, `tests/test_store.py`.
2. **CLI:** `cli.py`, `tests/test_cli.py`, README setup/run instructions, and the `Run:` command
   in CLAUDE.md.

## Out of scope (later phases)
Priorities, tags, due dates, reminders, recurring tasks, search, filter, sort, persistence (files
or a database), multiple users.
