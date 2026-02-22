"""Sandpiper MCPサーバー"""

from mcp.server.fastmcp import FastMCP

from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

mcp = FastMCP("sandpiper")


@mcp.tool()
def get_in_progress_todos() -> list[dict[str, str | None]]:
    """現在進行中(IN_PROGRESS)のToDoリストを取得する"""
    repo = NotionTodoRepository()
    todos = repo.find_by_status(ToDoStatusEnum.IN_PROGRESS)
    return [
        {
            "id": todo.id,
            "title": todo.title,
            "status": todo.status.value,
            "section": todo.section.value if todo.section else None,
            "log_start_datetime": todo.log_start_datetime.isoformat() if todo.log_start_datetime else None,
        }
        for todo in todos
    ]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
