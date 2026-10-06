"""Task data model. See specs/features/task-crud.md, "Task data"."""

from dataclasses import dataclass


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
