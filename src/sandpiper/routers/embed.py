"""Notion埋め込み用API"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

router = APIRouter(
    prefix="/embed",
    tags=["embed"],
)

# テンプレート設定
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/todo/in-progress", response_class=HTMLResponse)
async def get_in_progress_todo(request: Request) -> HTMLResponse:
    """IN_PROGRESSステータスのTODOを1件表示する

    Notionに埋め込むための画面。
    """
    todo_repository = NotionTodoRepository()
    todos = todo_repository.find_by_status(ToDoStatusEnum.IN_PROGRESS)

    # 1件だけ取得(なければNone)
    current_todo = todos[0] if todos else None

    return templates.TemplateResponse(
        "embed_todo.html",
        {
            "request": request,
            "todo": current_todo,
        },
    )
