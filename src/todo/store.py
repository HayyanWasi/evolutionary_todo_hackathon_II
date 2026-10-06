"""In-memory task storage. See specs/features/task-crud.md, "Design"."""

from todo.models import Task

MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000


class InvalidTaskError(ValueError):
    """A title or description breaks the validation rules."""


class TaskNotFoundError(LookupError):
    """No task has the given ID."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task #{task_id} not found.")
        self.task_id = task_id


def _clean_title(title: str) -> str:
    title = title.strip()
    if not title:
        raise InvalidTaskError("Title is required.")
    if len(title) > MAX_TITLE_LENGTH:
        raise InvalidTaskError(f"Title must be at most {MAX_TITLE_LENGTH} characters.")
    return title


def _clean_description(description: str) -> str:
    description = description.strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise InvalidTaskError(
            f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters."
        )
    return description


class TaskStore:
    """Holds tasks for one session. IDs start at 1 and are never reused."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, title: str, description: str = "") -> Task:
        task = Task(
            id=self._next_id,
            title=_clean_title(title),
            description=_clean_description(description),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    def get(self, task_id: int) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(task_id) from None

    def update(
        self, task_id: int, title: str | None = None, description: str | None = None
    ) -> Task:
        task = self.get(task_id)
        # Validate both fields before touching the task so a failed update changes nothing.
        new_title = task.title if title is None else _clean_title(title)
        new_description = (
            task.description if description is None else _clean_description(description)
        )
        task.title = new_title
        task.description = new_description
        return task

    def delete(self, task_id: int) -> Task:
        task = self.get(task_id)
        del self._tasks[task_id]
        return task

    def set_completed(self, task_id: int, completed: bool) -> Task:
        task = self.get(task_id)
        task.completed = completed
        return task
