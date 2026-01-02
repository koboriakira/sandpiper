"""メインアプリケーション"""

import typer
from rich.console import Console
from rich.panel import Panel

from sandpiper.app.app import bootstrap
from sandpiper.plan.application.create_todo import CreateNewToDoRequest

from . import __version__

app = typer.Typer(
    name="sandpiper",
    help="個人のタスク管理を支援するCLIアプリケーション",
    add_completion=False,
)
console = Console()

sandpiper_app = bootstrap()


@app.command()
def hello(name: str = typer.Option("World", help="挨拶する相手の名前")) -> None:
    """挨拶を表示します"""
    console.print(
        Panel(
            f"[bold green]こんにちは、{name}![/bold green]",
            title="Python Project 2026",
            border_style="blue",
        )
    )


@app.command()
def version() -> None:
    """バージョン情報を表示します"""
    console.print(f"Sandpiper version: [bold]{__version__}[/bold]")


@app.command()
def create_todo(title: str, start: bool = typer.Option(False, help="タスクをすぐに開始するかどうか")) -> None:
    """新しいToDoタスクを作成します"""
    sandpiper_app.create_todo.execute(
        request=CreateNewToDoRequest(
            title=title,
        ),
        enableStart=start,
    )


@app.command()
def create_repeat_project_tasks() -> None:
    """繰り返しのプロジェクトタスクを作成します"""
    sandpiper_app.create_repeat_project_task.execute()


@app.command()
def get_todo_log() -> None:
    """完了したToDoタスクのログを取得します"""
    result = sandpiper_app.get_todo_log.execute()
    for todo in result:
        console.print(
            f"- {todo.title} ({todo.perform_range[0].strftime('%Y-%m-%d %H:%M')} - {todo.perform_range[1].strftime('%Y-%m-%d %H:%M')})"
        )


@app.command()
def create_repeat_tasks(
    basis_date: str = typer.Option(..., help="繰り返しタスクを作成する基準日 (YYYY-MM-DD形式)"),
) -> None:
    """繰り返しタスクを作成します"""
    from datetime import datetime

    try:
        date_obj = datetime.strptime(basis_date, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
        raise typer.Exit(code=1)

    sandpiper_app.create_repeat_task.execute(basis_date=date_obj)


if __name__ == "__main__":
    app()
