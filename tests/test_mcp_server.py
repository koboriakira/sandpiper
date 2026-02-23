"""MCPサーバーのテスト"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from sandpiper.perform.domain.todo import ToDo
from sandpiper.review.query.activity_log_item import ActivityLogItem, ActivityType
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

JST = ZoneInfo("Asia/Tokyo")


def _make_todo(
    id: str = "page-id-1",
    title: str = "テストタスク",
    status: ToDoStatusEnum = ToDoStatusEnum.IN_PROGRESS,
    section: TaskChuteSection | None = TaskChuteSection.B_10_13,
    log_start_datetime: datetime | None = None,
) -> ToDo:
    return ToDo(
        id=id,
        title=title,
        status=status,
        section=section,
        log_start_datetime=log_start_datetime or datetime(2026, 2, 23, 10, 0, tzinfo=JST),
    )


class TestSerializeTodo:
    """_serialize_todoヘルパー関数のテスト"""

    def test_serializes_all_fields(self) -> None:
        from sandpiper.mcp_server import _serialize_todo

        todo = _make_todo()
        result = _serialize_todo(todo)

        assert result["id"] == "page-id-1"
        assert result["title"] == "テストタスク"
        assert result["status"] == "InProgress"
        assert result["section"] == "B_10_13"
        assert result["log_start_datetime"] == "2026-02-23T10:00:00+09:00"

    def test_serializes_none_fields(self) -> None:
        from sandpiper.mcp_server import _serialize_todo

        todo = _make_todo(section=None, log_start_datetime=None)
        todo.log_start_datetime = None
        result = _serialize_todo(todo)

        assert result["section"] is None
        assert result["log_start_datetime"] is None


class TestGetInProgressTodos:
    """get_in_progress_todosツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_returns_in_progress_todos(self, mock_repo_cls: MagicMock) -> None:
        """IN_PROGRESSのToDoが正しく返されるケース"""
        from sandpiper.mcp_server import get_in_progress_todos

        todo = _make_todo()
        mock_repo_cls.return_value.find_by_status.return_value = [todo]

        result = get_in_progress_todos()

        mock_repo_cls.return_value.find_by_status.assert_called_once()
        args = mock_repo_cls.return_value.find_by_status.call_args[0]
        assert args[0].value == ToDoStatusEnum.IN_PROGRESS.value
        assert len(result) == 1
        assert result[0]["id"] == "page-id-1"
        assert result[0]["title"] == "テストタスク"
        assert result[0]["status"] == "InProgress"
        assert result[0]["section"] == "B_10_13"
        assert result[0]["log_start_datetime"] == "2026-02-23T10:00:00+09:00"

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_returns_empty_list(self, mock_repo_cls: MagicMock) -> None:
        """空リストのケース"""
        from sandpiper.mcp_server import get_in_progress_todos

        mock_repo_cls.return_value.find_by_status.return_value = []

        result = get_in_progress_todos()

        assert result == []

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_handles_none_fields(self, mock_repo_cls: MagicMock) -> None:
        """section、log_start_datetimeがNoneのケース"""
        from sandpiper.mcp_server import get_in_progress_todos

        todo = _make_todo(section=None, log_start_datetime=None)
        todo.log_start_datetime = None
        mock_repo_cls.return_value.find_by_status.return_value = [todo]

        result = get_in_progress_todos()

        assert result[0]["section"] is None
        assert result[0]["log_start_datetime"] is None


class TestGetPendingTodos:
    """get_pending_todosツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_returns_pending_todos(self, mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_pending_todos

        todo = _make_todo(status=ToDoStatusEnum.TODO)
        mock_repo_cls.return_value.find_by_status.return_value = [todo]

        result = get_pending_todos()

        args = mock_repo_cls.return_value.find_by_status.call_args[0]
        assert args[0].value == ToDoStatusEnum.TODO.value
        assert len(result) == 1
        assert result[0]["status"] == "ToDo"

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_returns_empty_list(self, mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_pending_todos

        mock_repo_cls.return_value.find_by_status.return_value = []

        result = get_pending_todos()

        assert result == []


class TestGetDoneTodos:
    """get_done_todosツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionTodoQuery")
    def test_returns_done_todos(self, mock_query_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_done_todos

        activity = ActivityLogItem(
            activity_type=ActivityType.TODO,
            title="完了タスク",
            start_datetime=datetime(2026, 2, 23, 10, 0, tzinfo=JST),
            end_datetime=datetime(2026, 2, 23, 11, 0, tzinfo=JST),
            kind="routine",
            project_name="",
        )
        mock_query_cls.return_value.fetch_done_todos_by_date.return_value = [activity]

        result = get_done_todos(target_date="2026-02-23")

        mock_query_cls.return_value.fetch_done_todos_by_date.assert_called_once_with(date(2026, 2, 23))
        assert len(result) == 1
        assert result[0]["title"] == "完了タスク"
        assert result[0]["start_datetime"] == "2026-02-23T10:00:00+09:00"
        assert result[0]["end_datetime"] == "2026-02-23T11:00:00+09:00"
        assert result[0]["duration_minutes"] == 60

    @patch("sandpiper.mcp_server.NotionTodoQuery")
    def test_uses_today_when_no_date(self, mock_query_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_done_todos

        mock_query_cls.return_value.fetch_done_todos_by_date.return_value = []

        result = get_done_todos()

        mock_query_cls.return_value.fetch_done_todos_by_date.assert_called_once()
        assert result == []


class TestGetTodo:
    """get_todoツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_returns_single_todo(self, mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_todo

        todo = _make_todo()
        mock_repo_cls.return_value.find.return_value = todo

        result = get_todo(page_id="page-id-1")

        mock_repo_cls.return_value.find.assert_called_once_with("page-id-1")
        assert result["id"] == "page-id-1"
        assert result["title"] == "テストタスク"


class TestCreateTodo:
    """create_todoツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionPlanTodoRepository")
    @patch("sandpiper.mcp_server.MessageDispatcher")
    @patch("sandpiper.mcp_server.EventBus")
    def test_creates_todo(
        self, _mock_bus_cls: MagicMock, _mock_dispatcher_cls: MagicMock, _mock_repo_cls: MagicMock
    ) -> None:
        from sandpiper.mcp_server import create_todo

        result = create_todo(title="新しいタスク")

        assert result["status"] == "created"
        assert result["title"] == "新しいタスク"

    @patch("sandpiper.mcp_server.NotionPlanTodoRepository")
    @patch("sandpiper.mcp_server.MessageDispatcher")
    @patch("sandpiper.mcp_server.EventBus")
    def test_creates_todo_with_start(
        self, _mock_bus_cls: MagicMock, _mock_dispatcher_cls: MagicMock, _mock_repo_cls: MagicMock
    ) -> None:
        from sandpiper.mcp_server import create_todo

        result = create_todo(title="開始するタスク", start=True)

        assert result["status"] == "created"
        assert result["started"] is True


class TestStartTodo:
    """start_todoツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionSharedProjectTaskRepository")
    @patch("sandpiper.mcp_server.NotionTodoRepository")
    @patch("sandpiper.mcp_server.MessageDispatcher")
    @patch("sandpiper.mcp_server.EventBus")
    def test_starts_todo(
        self,
        _mock_bus_cls: MagicMock,
        _mock_dispatcher_cls: MagicMock,
        _mock_repo_cls: MagicMock,
        _mock_pt_repo_cls: MagicMock,
    ) -> None:
        from sandpiper.mcp_server import start_todo

        result = start_todo(page_id="page-id-1")

        assert result["status"] == "started"
        assert result["page_id"] == "page-id-1"


class TestCompleteTodo:
    """complete_todoツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    @patch("sandpiper.mcp_server.MessageDispatcher")
    @patch("sandpiper.mcp_server.EventBus")
    def test_completes_todo(
        self, _mock_bus_cls: MagicMock, _mock_dispatcher_cls: MagicMock, _mock_repo_cls: MagicMock
    ) -> None:
        from sandpiper.mcp_server import complete_todo

        result = complete_todo(page_id="page-id-1")

        assert result["status"] == "completed"
        assert result["page_id"] == "page-id-1"


class TestGetUndoneProjectTasks:
    """get_undone_project_tasksツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionProjectTaskQuery")
    def test_returns_undone_project_tasks(self, mock_query_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_undone_project_tasks
        from sandpiper.plan.query.project_task_dto import ProjectTaskDto

        dto = ProjectTaskDto(
            page_id="pt-id-1",
            title="プロジェクトタスク",
            status=ToDoStatusEnum.IN_PROGRESS,
            project_page_id="proj-id-1",
            is_next=True,
            context=["仕事"],
        )
        mock_query_cls.return_value.fetch_undone_project_tasks.return_value = [dto]

        result = get_undone_project_tasks()

        assert len(result) == 1
        assert result[0]["page_id"] == "pt-id-1"
        assert result[0]["title"] == "プロジェクトタスク"
        assert result[0]["status"] == "InProgress"
        assert result[0]["is_next"] is True


class TestCreateProject:
    """create_projectツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionProjectRepository")
    def test_creates_project(self, _mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import create_project

        result = create_project(name="新プロジェクト", start_date="2026-03-01")

        assert result["status"] == "created"
        assert result["name"] == "新プロジェクト"

    @patch("sandpiper.mcp_server.NotionProjectRepository")
    def test_creates_project_with_end_date(self, _mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import create_project

        result = create_project(name="期限付き", start_date="2026-03-01", end_date="2026-03-31")

        assert result["status"] == "created"


class TestCreateProjectTask:
    """create_project_taskツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionSharedProjectTaskRepository")
    def test_creates_project_task(self, _mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import create_project_task

        result = create_project_task(title="新タスク", project_id="proj-id-1")

        assert result["status"] == "created"
        assert result["title"] == "新タスク"


class TestGetSomedayItems:
    """get_someday_itemsツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionSomedayRepository")
    def test_returns_someday_items(self, mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_someday_items
        from sandpiper.shared.model.someday_item import SomedayItem
        from sandpiper.shared.valueobject.someday_timing import SomedayTiming

        item = SomedayItem(
            id="sd-id-1",
            title="いつかやること",
            timing=SomedayTiming.SOMEDAY,
            do_tomorrow=False,
            context=["個人"],
        )
        mock_repo_cls.return_value.fetch_all.return_value = [item]

        result = get_someday_items()

        assert len(result) == 1
        assert result[0]["id"] == "sd-id-1"
        assert result[0]["title"] == "いつかやること"
        assert result[0]["timing"] == "いつか"
        assert result[0]["do_tomorrow"] is False


class TestGetTomorrowSomedayItems:
    """get_tomorrow_someday_itemsツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionSomedayRepository")
    def test_returns_tomorrow_items(self, mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import get_tomorrow_someday_items
        from sandpiper.shared.model.someday_item import SomedayItem
        from sandpiper.shared.valueobject.someday_timing import SomedayTiming

        item = SomedayItem(
            id="sd-id-2",
            title="明日やること",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=True,
        )
        mock_repo_cls.return_value.fetch_tomorrow_items.return_value = [item]

        result = get_tomorrow_someday_items()

        assert len(result) == 1
        assert result[0]["do_tomorrow"] is True


class TestCreateSomedayItem:
    """create_someday_itemツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionSomedayRepository")
    def test_creates_someday_item(self, mock_repo_cls: MagicMock) -> None:
        from sandpiper.mcp_server import create_someday_item
        from sandpiper.shared.model.someday_item import SomedayItem
        from sandpiper.shared.valueobject.someday_timing import SomedayTiming

        saved_item = SomedayItem(
            id="sd-new-1",
            title="新しいサムデイ",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=False,
        )
        mock_repo_cls.return_value.save.return_value = saved_item

        result = create_someday_item(title="新しいサムデイ")

        assert result["status"] == "created"
        assert result["id"] == "sd-new-1"
        assert result["title"] == "新しいサムデイ"
