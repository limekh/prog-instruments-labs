import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from main import (
    TaskManager, User, Task, Project, TaskStatus, Priority,
    NotificationService
)


def test_task_complete():
    user = User("u1", "Alice", "a@a.com")
    task = Task("t1", "Test", "desc", Priority.MEDIUM, user)
    task.complete()
    assert task.status == TaskStatus.DONE

def test_task_is_overdue():
    user = User("u1", "Alice", "a@a.com")
    past = datetime.now() - timedelta(days=1)
    task = Task("t1", "Late", "desc", Priority.HIGH, user, due_date=past)
    assert task.is_overdue() is True

    task.complete()
    assert task.is_overdue() is False


def test_user_creation_valid():
    user = User("u1", "Alice", "alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"


def test_user_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        User("u1", "Alice", "invalid-email")


def test_project_create_task_valid():
    owner = User("u1", "Alice", "a@a.com")
    assignee = User("u2", "Bob", "b@b.com")
    project = Project("p1", "Web App", owner)
    project.add_member(assignee)

    task = project.create_task(
        "t1", "Design UI", "Create mockups", Priority.MEDIUM, assignee
    )
    assert task in project.tasks
    assert task.assignee == assignee


def test_task_empty_title():
    user = User("u1", "Alice", "a@a.com")
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Task("t1", "   ", "desc", Priority.LOW, user)


@pytest.mark.parametrize("priority", [Priority.LOW, Priority.MEDIUM, Priority.HIGH])
def test_task_priority_assignment(priority):
    user = User("u1", "X", "x@x.com")
    task = Task("t1", "Test", "desc", priority, user)
    assert task.priority == priority


@pytest.mark.parametrize("email,valid", [
    ("test@example.com", True),
    ("user@domain.org", True),
    ("bad-email", False),
    ("", False),
    ("no-at.com", False),
])
def test_user_email_validation(email, valid):
    if valid:
        User("u1", "Test", email)
    else:
        with pytest.raises(ValueError):
            User("u1", "Test", email)


def test_project_sends_notification_on_task_create():
    mock_notifier = Mock(spec=NotificationService)
    owner = User("u1", "Alice", "a@a.com")
    assignee = User("u2", "Bob", "b@b.com")
    project = Project("p1", "App", owner)
    project.add_member(assignee)

    project.create_task(
        "t1", "New Task", "desc", Priority.HIGH, assignee,
        notify_on_create=True,
        notification_service=mock_notifier
    )

    mock_notifier.send_email.assert_called_once_with(
        to="b@b.com",
        subject="New task assigned: New Task",
        body="You have been assigned to task 'New Task' in project 'App'."
    )


def test_task_manager_project_with_no_tasks():
    tm = TaskManager()
    alice = tm.create_user("u1", "Alice", "a@a.com")
    proj = tm.create_project("p1", "Empty", alice)
    assert proj.get_completed_ratio() == 0.0
