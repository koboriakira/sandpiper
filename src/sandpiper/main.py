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
def create_repeat_project_tasks(
    tomorrow: bool = typer.Option(False, help="明日のタスクとして作成するかどうか"),
) -> None:
    """繰り返しのプロジェクトタスクを作成します"""
    sandpiper_app.create_repeat_project_task.execute(is_tomorrow=tomorrow)


@app.command()
@app.command()
def get_todo_log(
    json: bool = typer.Option(False, "--json", help="JSON形式で出力する"),
    markdown: bool = typer.Option(False, "--markdown", help="Markdown形式で出力する"),
) -> None:
    """完了したToDoタスクのログを取得します"""
    import json as _json

    result = sandpiper_app.get_todo_log.execute()
    if json:
        from typing import Any

        def todo_to_dict(todo: Any) -> dict[str, Any]:
            return {
                "title": todo.title,
                "kind": getattr(todo.kind, "value", str(todo.kind)),
                "project_name": todo.project_name,
                "perform_range": [
                    todo.perform_range[0].strftime("%Y-%m-%d %H:%M"),
                    todo.perform_range[1].strftime("%Y-%m-%d %H:%M"),
                ]
                if getattr(todo, "perform_range", None)
                else None,
            }

        todos_json = [todo_to_dict(todo) for todo in result]
        console.print(_json.dumps(todos_json, ensure_ascii=False, indent=2))
    elif markdown:
        lines = ["| タイトル | 種別 | プロジェクト | 実施期間 |", "| --- | --- | --- | --- |"]
        for todo in result:
            title = todo.title.replace("|", "\\|")
            kind = getattr(todo.kind, "value", str(todo.kind))
            project = todo.project_name.replace("|", "\\|") if todo.project_name else ""
            if getattr(todo, "perform_range", None):
                daterange = f"{todo.perform_range[0].strftime('%Y-%m-%d %H:%M')} - {todo.perform_range[1].strftime('%Y-%m-%d %H:%M')}"
            else:
                daterange = ""
            lines.append(f"| {title} | {kind} | {project} | {daterange} |")
        console.print("\n".join(lines))
    else:
        for todo in result:
            prefix = f"【{todo.kind.value} {todo.project_name}】" if todo.project_name else f"【{todo.kind.value}】"
            suffix_daterange = f" ({todo.perform_range[0].strftime('%Y-%m-%d %H:%M')} - {todo.perform_range[1].strftime('%Y-%m-%d %H:%M')})"
            console.print(f"- {prefix}{todo.title}{suffix_daterange}")


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
