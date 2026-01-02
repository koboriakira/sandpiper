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


if __name__ == "__main__":
    app()
