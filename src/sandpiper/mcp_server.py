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
from sandpiper.plan.domain.project import InsertedProject
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


def _serialize_project(project: InsertedProject) -> dict[str, str | None]:
    """InsertedProjectをdict変換する"""
    return {
        "id": project.id,
        "name": project.name,
        "start_date": project.start_date.isoformat(),
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "status": project.status.value if project.status else None,
        "jira_url": project.jira_url,
        "claude_url": project.claude_url,
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
    """現在取りかかっている作業の一覧を取得する。IN_PROGRESSステータスのタスクを返す。"""
    repo = NotionTodoRepository()
    todos = repo.find_by_status(ToDoStatusEnum.IN_PROGRESS)
    return [_serialize_todo(todo) for todo in todos]


@mcp.tool()
def get_pending_todos() -> list[dict[str, str | None]]:
    """まだ着手していないタスクの一覧を取得する。TODOステータスのタスクを返す。"""
    repo = NotionTodoRepository()
    todos = repo.find_by_status(ToDoStatusEnum.TODO)
    return [_serialize_todo(todo) for todo in todos]


@mcp.tool()
def get_done_todos(target_date: str | None = None) -> list[dict[str, str | int | None]]:
    """指定日に完了したタスクの実績を取得する。日報作成や振り返りに使う。

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
    """特定タスクの詳細情報を取得する。

    Args:
        page_id: タスクのNotionページID
    """
    repo = NotionTodoRepository()
    todo = repo.find(page_id)
    return _serialize_todo(todo)


@mcp.tool()
def get_undone_project_tasks() -> list[dict[str, str | bool | list[str] | None]]:
    """プロジェクトの未完了タスク一覧を取得する。"""
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
def get_projects(status: str | None = None) -> list[dict[str, str | None]]:
    """プロジェクト一覧を取得する。タスク追加時のプロジェクトID確認に使う。

    Args:
        status: ステータスでフィルタ(ToDo, InProgress, Done等)。省略時はDone以外を返す。
    """
    repo = NotionProjectRepository()
    projects = repo.fetch_all()
    if status is not None:
        target = ToDoStatusEnum(status)
        projects = [p for p in projects if p.status == target]
    else:
        projects = [p for p in projects if p.status != ToDoStatusEnum.DONE]
    return [_serialize_project(p) for p in projects]


@mcp.tool()
def get_someday_items() -> list[dict[str, str | bool | list[str] | None]]:
    """サムデイリスト全体を取得する。いつかやりたいことの一覧。"""
    repo = NotionSomedayRepository()
    items = repo.fetch_all()
    return [_serialize_someday_item(item) for item in items]


@mcp.tool()
def get_tomorrow_someday_items() -> list[dict[str, str | bool | list[str] | None]]:
    """明日やる候補としてマークされたサムデイアイテムを取得する。"""
    repo = NotionSomedayRepository()
    items = repo.fetch_tomorrow_items()
    return [_serialize_someday_item(item) for item in items]


# ── 書き込み系ツール ─────────────────────────────────────


@mcp.tool()
def schedule_task(title: str, section: str | None = None) -> dict[str, str]:
    """今日のタスクリストに新しいタスクを追加する。まだ開始しない。

    予定として配置するためのツール。タスクを開始するには別途 begin_task を使う。
    いますぐ取りかかる割り込み作業には interrupt_with_task を使うこと。

    Args:
        title: タスクのタイトル
        section: 時間帯セクション(A_07_10, B_10_13, C_13_17, D_17_19, E_19_22, F_22_24, G_24_07)。省略時は未指定。
    """
    from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection

    event_bus = EventBus()
    dispatcher = MessageDispatcher(event_bus)
    repo = NotionPlanTodoRepository()
    use_case = CreateToDo(dispatcher=dispatcher, todo_repository=repo)

    section_val = TaskChuteSection(section) if section else None
    request = CreateNewToDoRequest(title=title, section=section_val)
    use_case.execute(request)

    return {"status": "created", "title": title}


@mcp.tool()
def interrupt_with_task(title: str) -> dict[str, str | bool]:
    """割り込みタスクを作成し即座に開始する。

    今の作業を中断して別のことに取りかかる場面で使う。
    セクションと並び順は現在時刻から自動決定される。
    計画的にタスクを追加したい場合は schedule_task を使うこと。

    Args:
        title: タスクのタイトル
    """
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
def begin_task(page_id: str) -> dict[str, str]:
    """作成済みのタスクを開始する。ステータスをIN_PROGRESSに変更する。

    schedule_task で追加したタスクに着手するときに使う。
    新しいタスクの作成はできない。作成には schedule_task を使うこと。

    Args:
        page_id: 開始するタスクのNotionページID
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
def finish_task(page_id: str) -> dict[str, str]:
    """実行中のタスクを完了にする。ステータスをDONEに変更する。

    完了時にSlack通知が自動送信される。

    Args:
        page_id: 完了するタスクのNotionページID
    """
    event_bus = EventBus()
    dispatcher = MessageDispatcher(event_bus)
    todo_repo = NotionTodoRepository()
    use_case = CompleteTodoUseCase(todo_repository=todo_repo, dispatcher=dispatcher)
    use_case.execute(page_id)
    return {"status": "completed", "page_id": page_id}


@mcp.tool()
def create_project(name: str, start_date: str, end_date: str | None = None) -> dict[str, str]:
    """新しいプロジェクトを作成する。

    複数タスクをまとめる上位概念。プロジェクト配下の個別タスク追加には add_task_to_project を使う。

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
def add_task_to_project(title: str, project_id: str) -> dict[str, str]:
    """既存プロジェクトにタスクを追加する。

    プロジェクトIDが必須。プロジェクトに紐づかない日常タスクには schedule_task を使うこと。

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
def defer_to_someday(
    title: str,
    timing: str = "明日",
    do_tomorrow: bool = False,
    context: list[str] | None = None,
) -> dict[str, str | bool | list[str]]:
    """いつかやりたいことをサムデイリストに保存する。

    今日すぐやらないが忘れたくないことに使う。
    今日のタスクとして追加したい場合は schedule_task を使うこと。

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


@mcp.tool()
def prepare_tomorrow_todos() -> dict[str, str]:
    """明日のTODOリストを一括作成する。

    「明日のTODOを作成して」「TODOリストを準備して」などの指示で呼び出す。
    ルーチンタスク、プロジェクトタスク、サムデイリスト、カレンダーイベントから
    TODOを自動生成する。対象日の判定(明日か今日か)はシステムが現在時刻から
    自動で行うため、ユーザーの指示に関わらず常にこのツールを呼び出せばよい。
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from sandpiper.perform.application.mark_remaining_todos_as_today import MarkRemainingTodosAsToday
    from sandpiper.perform.infrastructure.notion_todo_repository import (
        NotionTodoRepository as PerformNotionTodoRepository,
    )
    from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask
    from sandpiper.plan.application.create_repeat_task import CreateRepeatTask
    from sandpiper.plan.application.create_schedule_tasks import CreateScheduleTasks
    from sandpiper.plan.application.create_tasks_by_someday_list import CreateTasksBySomedayList
    from sandpiper.plan.application.prepare_tomorrow_todos import PrepareTomorrowTodos
    from sandpiper.plan.infrastructure.notion_routine_repository import NotionRoutineRepository
    from sandpiper.plan.infrastructure.notion_someday_repository import NotionSomedayRepository
    from sandpiper.plan.query.calendar_event_query import NotionCalendarEventQuery
    from sandpiper.plan.query.project_task_query import NotionProjectTaskQuery
    from sandpiper.plan.query.todo_query import NotionTodoQuery as PlanNotionTodoQuery
    from sandpiper.shared.infrastructure.archive_deleted_pages import ArchiveDeletedPages

    jst = ZoneInfo("Asia/Tokyo")
    now_jst = datetime.now(jst)

    is_tomorrow, basis_date = PrepareTomorrowTodos.resolve_params_from_now(now_hour=now_jst.hour, today=now_jst.date())

    plan_todo_repo = NotionPlanTodoRepository()
    plan_todo_query = PlanNotionTodoQuery()
    perform_todo_repo = PerformNotionTodoRepository()
    use_case = PrepareTomorrowTodos(
        mark_remaining_todos_as_today=MarkRemainingTodosAsToday(
            todo_repository=perform_todo_repo,
        ),
        create_repeat_project_task=CreateRepeatProjectTask(
            project_task_query=NotionProjectTaskQuery(),
            todo_repository=plan_todo_repo,
        ),
        create_repeat_task=CreateRepeatTask(
            routine_repository=NotionRoutineRepository(),
            todo_repository=plan_todo_repo,
            todo_query=plan_todo_query,
        ),
        create_tasks_by_someday_list=CreateTasksBySomedayList(
            someday_repository=NotionSomedayRepository(),
            todo_repository=plan_todo_repo,
        ),
        create_schedule_tasks=CreateScheduleTasks(
            calendar_event_query=NotionCalendarEventQuery(),
            todo_repository=plan_todo_repo,
            todo_query=plan_todo_query,
        ),
        archive_deleted_pages=ArchiveDeletedPages(),
    )

    result = use_case.execute(is_tomorrow=is_tomorrow, basis_date=basis_date)
    return {
        "status": "completed",
        "summary": result.summary,
        "basis_date": result.basis_date.isoformat(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
