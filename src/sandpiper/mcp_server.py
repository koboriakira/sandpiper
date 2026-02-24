"""Sandpiper MCPサーバー"""

from datetime import date

from mcp.server.fastmcp import FastMCP

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.application.complete_todo import CompleteTodo as CompleteTodoUseCase
from sandpiper.perform.application.start_todo import StartTodo as StartTodoUseCase
from sandpiper.perform.domain.todo import ToDo
from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.plan.application.create_project import CreateProject, CreateProjectRequest
from sandpiper.plan.application.create_project_task import CreateProjectTask, CreateProjectTaskRequest
from sandpiper.plan.application.create_someday_item import CreateSomedayItem, CreateSomedayItemRequest
from sandpiper.plan.application.create_todo import CreateNewToDoRequest, CreateToDo
from sandpiper.plan.infrastructure.notion_project_repository import NotionProjectRepository
from sandpiper.plan.infrastructure.notion_project_task_repository import (
    NotionProjectTaskRepository as NotionSharedProjectTaskRepository,
)
from sandpiper.plan.infrastructure.notion_someday_repository import NotionSomedayRepository
from sandpiper.plan.infrastructure.notion_todo_repository import NotionTodoRepository as NotionPlanTodoRepository
from sandpiper.plan.query.project_task_query import NotionProjectTaskQuery
from sandpiper.review.query.todo_query import NotionTodoQuery
from sandpiper.shared.infrastructure.event_bus import EventBus
from sandpiper.shared.model.someday_item import SomedayItem
from sandpiper.shared.utils.date_utils import jst_now, jst_today
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

mcp = FastMCP("sandpiper")


# ── シリアライズヘルパー ──────────────────────────────────


def _serialize_todo(todo: ToDo) -> dict[str, str | None]:
    """perform側のToDoをdict変換する"""
    return {
        "id": todo.id,
        "title": todo.title,
        "status": todo.status.value,
        "section": todo.section.value if todo.section else None,
        "log_start_datetime": todo.log_start_datetime.isoformat() if todo.log_start_datetime else None,
    }


def _serialize_someday_item(item: SomedayItem) -> dict[str, str | bool | list[str] | None]:
    """SomedayItemをdict変換する"""
    return {
        "id": item.id,
        "title": item.title,
        "timing": item.timing.value,
        "do_tomorrow": item.do_tomorrow,
        "context": item.context,
    }


# ── 読み取り系ツール ─────────────────────────────────────


@mcp.tool()
def get_in_progress_todos() -> list[dict[str, str | None]]:
    """現在進行中(IN_PROGRESS)のToDoリストを取得する"""
    repo = NotionTodoRepository()
    todos = repo.find_by_status(ToDoStatusEnum.IN_PROGRESS)
    return [_serialize_todo(todo) for todo in todos]


@mcp.tool()
def get_pending_todos() -> list[dict[str, str | None]]:
    """未実施(TODO)のToDoリストを取得する"""
    repo = NotionTodoRepository()
    todos = repo.find_by_status(ToDoStatusEnum.TODO)
    return [_serialize_todo(todo) for todo in todos]


@mcp.tool()
def get_done_todos(target_date: str | None = None) -> list[dict[str, str | int | None]]:
    """指定日の完了ToDo一覧を取得する

    Args:
        target_date: 対象日(YYYY-MM-DD形式)。省略時は今日。
    """
    d = date.fromisoformat(target_date) if target_date else jst_today()
    query = NotionTodoQuery()
    items = query.fetch_done_todos_by_date(d)
    return [
        {
            "title": item.title,
            "start_datetime": item.start_datetime.isoformat(),
            "end_datetime": item.end_datetime.isoformat(),
            "duration_minutes": item.duration_minutes,
            "kind": item.kind,
            "project_name": item.project_name or None,
        }
        for item in items
    ]


@mcp.tool()
def get_todo(page_id: str) -> dict[str, str | None]:
    """単一ToDoの詳細を取得する

    Args:
        page_id: NotionページID
    """
    repo = NotionTodoRepository()
    todo = repo.find(page_id)
    return _serialize_todo(todo)


@mcp.tool()
def get_undone_project_tasks() -> list[dict[str, str | bool | list[str] | None]]:
    """未完了プロジェクトタスク一覧を取得する"""
    query = NotionProjectTaskQuery()
    dtos = query.fetch_undone_project_tasks()
    return [
        {
            "page_id": dto.page_id,
            "title": dto.title,
            "status": dto.status.value,
            "project_page_id": dto.project_page_id,
            "is_next": dto.is_next,
            "context": dto.context,
            "sort_order": dto.sort_order,
        }
        for dto in dtos
    ]


@mcp.tool()
def get_someday_items() -> list[dict[str, str | bool | list[str] | None]]:
    """サムデイリスト一覧を取得する"""
    repo = NotionSomedayRepository()
    items = repo.fetch_all()
    return [_serialize_someday_item(item) for item in items]


@mcp.tool()
def get_tomorrow_someday_items() -> list[dict[str, str | bool | list[str] | None]]:
    """明日やるサムデイアイテムを取得する"""
    repo = NotionSomedayRepository()
    items = repo.fetch_tomorrow_items()
    return [_serialize_someday_item(item) for item in items]


# ── 書き込み系ツール ─────────────────────────────────────


@mcp.tool()
def create_todo(title: str, section: str | None = None, start: bool = False) -> dict[str, str | bool]:
    """新しいToDoを作成する

    Args:
        title: タスクのタイトル
        section: セクション(A_07_10, B_10_13, C_13_17, D_17_19, E_19_22, F_22_24, G_24_07)
        start: 作成と同時に開始するか
    """
    from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection

    event_bus = EventBus()
    dispatcher = MessageDispatcher(event_bus)
    repo = NotionPlanTodoRepository()
    use_case = CreateToDo(dispatcher=dispatcher, todo_repository=repo)

    section_val = TaskChuteSection(section) if section else None
    request = CreateNewToDoRequest(title=title, section=section_val)
    use_case.execute(request, enableStart=start)

    return {"status": "created", "title": title, "started": start}


@mcp.tool()
def create_next_todo(title: str) -> dict[str, str | bool]:
    """差し込みタスクを作成して即座に開始する。現在時刻からセクションと並び順を自動決定する。"""
    from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
    from sandpiper.shared.valueobject.todo_kind import ToDoKind

    now = jst_now()
    current_section = TaskChuteSection.new(now)
    sort_order = now.strftime("%H:%M")

    event_bus = EventBus()
    dispatcher = MessageDispatcher(event_bus)
    repo = NotionPlanTodoRepository()
    use_case = CreateToDo(dispatcher=dispatcher, todo_repository=repo)

    request = CreateNewToDoRequest(
        title=title,
        kind=ToDoKind.INTERRUPTION,
        section=current_section,
        sort_order=sort_order,
    )
    use_case.execute(request, enableStart=True)

    return {"status": "created", "title": title, "started": True}


@mcp.tool()
def start_todo(page_id: str) -> dict[str, str]:
    """ToDoを開始(IN_PROGRESS)にする

    Args:
        page_id: NotionページID
    """
    event_bus = EventBus()
    dispatcher = MessageDispatcher(event_bus)
    todo_repo = NotionTodoRepository()
    pt_repo = NotionSharedProjectTaskRepository()
    use_case = StartTodoUseCase(
        todo_repository=todo_repo,
        project_task_repository=pt_repo,
        dispatcher=dispatcher,
    )
    use_case.execute(page_id)
    return {"status": "started", "page_id": page_id}


@mcp.tool()
def complete_todo(page_id: str) -> dict[str, str]:
    """ToDoを完了(DONE)にする

    Args:
        page_id: NotionページID
    """
    event_bus = EventBus()
    dispatcher = MessageDispatcher(event_bus)
    todo_repo = NotionTodoRepository()
    use_case = CompleteTodoUseCase(todo_repository=todo_repo, dispatcher=dispatcher)
    use_case.execute(page_id)
    return {"status": "completed", "page_id": page_id}


@mcp.tool()
def create_project(name: str, start_date: str, end_date: str | None = None) -> dict[str, str]:
    """新規プロジェクトを作成する

    Args:
        name: プロジェクト名
        start_date: 開始日(YYYY-MM-DD形式)
        end_date: 終了日(YYYY-MM-DD形式、省略可)
    """
    repo = NotionProjectRepository()
    use_case = CreateProject(project_repository=repo)
    request = CreateProjectRequest(
        name=name,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date) if end_date else None,
    )
    use_case.execute(request)
    return {"status": "created", "name": name}


@mcp.tool()
def create_project_task(title: str, project_id: str) -> dict[str, str]:
    """プロジェクトタスクを作成する

    Args:
        title: タスクのタイトル
        project_id: プロジェクトのNotionページID
    """
    repo = NotionSharedProjectTaskRepository()
    use_case = CreateProjectTask(project_task_repository=repo)
    request = CreateProjectTaskRequest(title=title, project_id=project_id)
    use_case.execute(request)
    return {"status": "created", "title": title, "project_id": project_id}


@mcp.tool()
def create_someday_item(
    title: str,
    timing: str = "明日",
    do_tomorrow: bool = False,
    context: list[str] | None = None,
) -> dict[str, str | bool | list[str]]:
    """サムデイアイテムを作成する

    Args:
        title: アイテムのタイトル
        timing: タイミング(明日, いつか, ついでに)
        do_tomorrow: 明日やるフラグ
        context: コンテクストのリスト
    """
    from sandpiper.shared.valueobject.someday_timing import SomedayTiming

    repo = NotionSomedayRepository()
    use_case = CreateSomedayItem(someday_repository=repo)
    request = CreateSomedayItemRequest(
        title=title,
        timing=SomedayTiming(timing),
        do_tomorrow=do_tomorrow,
        context=context or [],
    )
    result = use_case.execute(request)
    return {
        "status": "created",
        "id": result.id,
        "title": result.title,
        "timing": result.timing,
        "do_tomorrow": result.do_tomorrow,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
