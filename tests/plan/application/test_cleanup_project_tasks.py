"""プロジェクトタスク自動整理のテスト"""

from datetime import date

from sandpiper.plan.application.cleanup_project_tasks import CleanupProjectTasks
from sandpiper.plan.domain.project import InsertedProject
from sandpiper.shared.repository.project_task_repository import InsertedProjectTask
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class FakeProjectTaskRepository:
    def __init__(self, tasks: list[InsertedProjectTask] | None = None) -> None:
        self._tasks = tasks or []
        self.updated_statuses: list[tuple[str, ToDoStatusEnum]] = []
        self.deleted_ids: list[str] = []

    def fetch_not_done(self) -> list[InsertedProjectTask]:
        return self._tasks

    def update_status(self, page_id: str, status: ToDoStatusEnum) -> None:
        self.updated_statuses.append((page_id, status))

    def delete(self, page_id: str) -> None:
        self.deleted_ids.append(page_id)

    def save(self, project_task):
        pass

    def find(self, page_id: str) -> InsertedProjectTask:
        raise NotImplementedError


class FakeProjectRepository:
    def __init__(self, projects: list[InsertedProject] | None = None) -> None:
        self._projects = projects or []

    def fetch_all(self) -> list[InsertedProject]:
        return self._projects

    def save(self, project):
        pass

    def find(self, page_id: str):
        raise NotImplementedError

    def find_by_jira_url(self, _jira_url: str):
        return None

    def fetch_all_jira_urls(self) -> set[str]:
        return set()

    def fetch_projects_with_jira_url(self) -> list[InsertedProject]:
        return []

    def update_status(self, page_id: str, status: ToDoStatusEnum) -> None:
        pass


def _make_project(id: str, status: ToDoStatusEnum | None = None) -> InsertedProject:
    return InsertedProject(
        id=id,
        name=f"Project {id}",
        start_date=date(2026, 1, 1),
        status=status,
    )


def _make_task(id: str, project_id: str, status: ToDoStatusEnum = ToDoStatusEnum.TODO) -> InsertedProjectTask:
    return InsertedProjectTask(
        id=id,
        title=f"Task {id}",
        status=status,
        project_id=project_id,
    )


class TestCleanupProjectTasks:
    """CleanupProjectTasks ユースケースのテスト"""

    def test_parent_done_then_task_done(self) -> None:
        """親プロジェクトがDone → タスクもDoneに更新"""
        project = _make_project("proj-1", status=ToDoStatusEnum.DONE)
        task = _make_task("task-1", project_id="proj-1")

        task_repo = FakeProjectTaskRepository(tasks=[task])
        proj_repo = FakeProjectRepository(projects=[project])
        usecase = CleanupProjectTasks(
            project_task_repository=task_repo,
            project_repository=proj_repo,
        )

        result = usecase.execute()

        assert result.completed_count == 1
        assert result.deleted_count == 0
        assert ("task-1", ToDoStatusEnum.DONE) in task_repo.updated_statuses
        assert "Task task-1" in result.completed_titles

    def test_parent_not_found_then_task_deleted(self) -> None:
        """親プロジェクトが存在しない → タスクを削除"""
        task = _make_task("task-1", project_id="nonexistent-proj")

        task_repo = FakeProjectTaskRepository(tasks=[task])
        proj_repo = FakeProjectRepository(projects=[])
        usecase = CleanupProjectTasks(
            project_task_repository=task_repo,
            project_repository=proj_repo,
        )

        result = usecase.execute()

        assert result.completed_count == 0
        assert result.deleted_count == 1
        assert "task-1" in task_repo.deleted_ids
        assert "Task task-1" in result.deleted_titles

    def test_parent_in_progress_then_skip(self) -> None:
        """親プロジェクトが進行中 → スキップ"""
        project = _make_project("proj-1", status=ToDoStatusEnum.IN_PROGRESS)
        task = _make_task("task-1", project_id="proj-1")

        task_repo = FakeProjectTaskRepository(tasks=[task])
        proj_repo = FakeProjectRepository(projects=[project])
        usecase = CleanupProjectTasks(
            project_task_repository=task_repo,
            project_repository=proj_repo,
        )

        result = usecase.execute()

        assert result.completed_count == 0
        assert result.deleted_count == 0
        assert task_repo.updated_statuses == []
        assert task_repo.deleted_ids == []

    def test_mixed_cases(self) -> None:
        """混合ケース: Done親, 存在しない親, 進行中親"""
        done_project = _make_project("proj-done", status=ToDoStatusEnum.DONE)
        active_project = _make_project("proj-active", status=ToDoStatusEnum.TODO)

        task_done_parent = _make_task("task-1", project_id="proj-done")
        task_orphan = _make_task("task-2", project_id="proj-deleted")
        task_active = _make_task("task-3", project_id="proj-active")

        task_repo = FakeProjectTaskRepository(tasks=[task_done_parent, task_orphan, task_active])
        proj_repo = FakeProjectRepository(projects=[done_project, active_project])
        usecase = CleanupProjectTasks(
            project_task_repository=task_repo,
            project_repository=proj_repo,
        )

        result = usecase.execute()

        assert result.completed_count == 1
        assert result.deleted_count == 1
        assert ("task-1", ToDoStatusEnum.DONE) in task_repo.updated_statuses
        assert "task-2" in task_repo.deleted_ids

    def test_no_tasks_returns_zero(self) -> None:
        """タスクが0件の場合"""
        task_repo = FakeProjectTaskRepository(tasks=[])
        proj_repo = FakeProjectRepository(projects=[])
        usecase = CleanupProjectTasks(
            project_task_repository=task_repo,
            project_repository=proj_repo,
        )

        result = usecase.execute()

        assert result.completed_count == 0
        assert result.deleted_count == 0

    def test_empty_project_id_then_deleted(self) -> None:
        """project_idが空文字のタスク → 削除"""
        task = _make_task("task-1", project_id="")

        task_repo = FakeProjectTaskRepository(tasks=[task])
        proj_repo = FakeProjectRepository(projects=[])
        usecase = CleanupProjectTasks(
            project_task_repository=task_repo,
            project_repository=proj_repo,
        )

        result = usecase.execute()

        assert result.deleted_count == 1
        assert "task-1" in task_repo.deleted_ids
