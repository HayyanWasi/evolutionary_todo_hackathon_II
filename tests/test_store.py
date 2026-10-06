import pytest

from todo.store import InvalidTaskError, TaskNotFoundError, TaskStore


@pytest.fixture
def store() -> TaskStore:
    return TaskStore()


# --- Add ---


def test_add_assigns_sequential_ids(store):
    ids = [store.add(title).id for title in ("a", "b", "c")]
    assert ids == [1, 2, 3]


def test_add_sets_defaults(store):
    task = store.add("Buy milk")
    assert task.description == ""
    assert task.completed is False


def test_add_strips_whitespace(store):
    task = store.add("  Buy milk  ", "  2 litres  ")
    assert task.title == "Buy milk"
    assert task.description == "2 litres"


@pytest.mark.parametrize("title", ["", "   ", "\t\n"])
def test_add_rejects_blank_title(store, title):
    with pytest.raises(InvalidTaskError):
        store.add(title)
    assert store.list_tasks() == []


def test_add_rejects_title_over_200_chars(store):
    with pytest.raises(InvalidTaskError):
        store.add("x" * 201)


def test_add_rejects_description_over_1000_chars(store):
    with pytest.raises(InvalidTaskError):
        store.add("ok", "x" * 1001)


def test_add_accepts_exact_limits(store):
    task = store.add("x" * 200, "y" * 1000)
    assert len(task.title) == 200
    assert len(task.description) == 1000


def test_failed_add_does_not_consume_an_id(store):
    with pytest.raises(InvalidTaskError):
        store.add("")
    assert store.add("ok").id == 1


# --- View ---


def test_list_is_empty_initially(store):
    assert store.list_tasks() == []


def test_list_returns_tasks_in_creation_order(store):
    store.add("first")
    store.add("second")
    store.add("third")
    store.delete(2)
    store.add("fourth")
    assert [t.title for t in store.list_tasks()] == ["first", "third", "fourth"]


# --- Delete ---


def test_delete_returns_and_removes_task(store):
    store.add("Buy milk")
    removed = store.delete(1)
    assert removed.title == "Buy milk"
    assert store.list_tasks() == []


def test_ids_are_not_reused_after_delete(store):
    store.add("a")
    store.add("b")
    store.delete(2)
    assert store.add("c").id == 3


# --- Update ---


def test_update_title_only_keeps_description(store):
    store.add("old", "desc")
    task = store.update(1, title="new")
    assert (task.title, task.description) == ("new", "desc")


def test_update_description_only_keeps_title(store):
    store.add("title", "old")
    task = store.update(1, description="new")
    assert (task.title, task.description) == ("title", "new")


def test_update_does_not_change_completed(store):
    store.add("title")
    store.set_completed(1, True)
    assert store.update(1, title="new").completed is True


def test_update_can_clear_description(store):
    store.add("title", "desc")
    assert store.update(1, description="").description == ""


def test_update_rejects_blank_title_and_changes_nothing(store):
    store.add("original", "desc")
    with pytest.raises(InvalidTaskError):
        store.update(1, title="   ")
    task = store.get(1)
    assert (task.title, task.description) == ("original", "desc")


def test_update_with_one_bad_field_applies_neither(store):
    store.add("original", "desc")
    with pytest.raises(InvalidTaskError):
        store.update(1, title="ok", description="x" * 1001)
    task = store.get(1)
    assert (task.title, task.description) == ("original", "desc")


# --- Mark complete / incomplete ---


def test_set_completed_marks_done_and_undone(store):
    store.add("task")
    assert store.set_completed(1, True).completed is True
    assert store.set_completed(1, False).completed is False


def test_set_completed_is_idempotent(store):
    store.add("task")
    store.set_completed(1, True)
    assert store.set_completed(1, True).completed is True


# --- Unknown IDs ---


@pytest.mark.parametrize(
    "call",
    [
        lambda s: s.get(99),
        lambda s: s.update(99, title="x"),
        lambda s: s.delete(99),
        lambda s: s.set_completed(99, True),
    ],
    ids=["get", "update", "delete", "set_completed"],
)
def test_unknown_id_raises_not_found(store, call):
    store.add("only task")
    with pytest.raises(TaskNotFoundError, match=r"Task #99 not found\."):
        call(store)
