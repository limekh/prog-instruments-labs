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


def test_user_creation_valid():
    user = User("u1", "Alice", "alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"


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
