from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Callable


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User:
    def __init__(self, user_id: str, name: str, email: str):
        if not email or "@" not in email:
            raise ValueError("Invalid email")
        self.user_id = user_id
        self.name = name
        self.email = email

    def __eq__(self, other):
        return isinstance(other, User) and self.user_id == other.user_id

    def __hash__(self):
        return hash(self.user_id)


class Task:
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: Priority,
        assignee: User,
        due_date: Optional[datetime] = None,
    ):
        if not title.strip():
            raise ValueError("Title cannot be empty")
        self.task_id = task_id
        self.title = title.strip()
        self.description = description
        self.priority = priority
        self.assignee = assignee
        self.due_date = due_date
        self.status = TaskStatus.TODO
        self.created_at = datetime.now()

    def complete(self):
        self.status = TaskStatus.DONE

    def start_work(self):
        if self.status == TaskStatus.TODO:
            self.status = TaskStatus.IN_PROGRESS

    def is_overdue(self) -> bool:
        if self.due_date is None:
            return False
        return self.status != TaskStatus.DONE and datetime.now() > self.due_date

    def __repr__(self):
        return f"Task(id={self.task_id}, title='{self.title}', status={self.status.value})"


class NotificationService:
    """Внешний сервис уведомлений — будет мокаться в тестах"""
    def send_email(self, to: str, subject: str, body: str):
        # В реальности отправляет email
        pass


class Project:
    def __init__(self, project_id: str, name: str, owner: User):
        self.project_id = project_id
        self.name = name
        self.owner = owner
        self.tasks: List[Task] = []
        self.members: List[User] = [owner]

    def add_member(self, user: User):
        if user not in self.members:
            self.members.append(user)

    def create_task(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: Priority,
        assignee: User,
        due_date: Optional[datetime] = None,
        notify_on_create: bool = False,
        notification_service: Optional[NotificationService] = None,
    ) -> Task:
        if assignee not in self.members:
            raise ValueError("Assignee is not a project member")

        task = Task(task_id, title, description, priority, assignee, due_date)
        self.tasks.append(task)

        if notify_on_create and notification_service:
            notification_service.send_email(
                to=assignee.email,
                subject=f"New task assigned: {title}",
                body=f"You have been assigned to task '{title}' in project '{self.name}'."
            )
        return task

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return [t for t in self.tasks if t.status == status]

    def get_overdue_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.is_overdue()]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        return [t for t in self.tasks if t.priority == priority]

    def get_tasks_for_user(self, user: User) -> List[Task]:
        return [t for t in self.tasks if t.assigntee == user]

    def get_completed_ratio(self) -> float:
        if not self.tasks:
            return 0.0
        completed = len(self.get_tasks_by_status(TaskStatus.DONE))
        return completed / len(self.tasks)


class TaskManager:
    def __init__(self):
        self.projects: List[Project] = []
        self.users: List[User] = []

    def create_user(self, user_id: str, name: str, email: str) -> User:
        user = User(user_id, name, email)
        self.users.append(user)
        return user

    def create_project(self, project_id: str, name: str, owner: User) -> Project:
        if owner not in self.users:
            raise ValueError("Owner must be a registered user")
        project = Project(project_id, name, owner)
        self.projects.append(project)
        return project

    def find_project(self, project_id: str) -> Optional[Project]:
        for p in self.projects:
            if p.project_id == project_id:
                return p
        return None

    def find_user(self, user_id: str) -> Optional[User]:
        for u in self.users:
            if u.user_id == user_id:
                return u
        return None

    def get_all_tasks(self) -> List[Task]:
        tasks = []
        for p in self.projects:
            tasks.extend(p.tasks)
        return tasks

    def get_overdue_tasks_across_projects(self) -> List[Task]:
        return [t for t in self.get_all_tasks() if t.is_overdue()]

    def get_average_completion_rate(self) -> float:
        if not self.projects:
            return 0.0
        total = sum(p.get_completed_ratio() for p in self.projects)
        return total / len(self.projects)
