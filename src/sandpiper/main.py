"""メインアプリケーション"""

from datetime import UTC

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from sandpiper.app.app import bootstrap
from sandpiper.plan.application.create_project_task import CreateProjectTaskRequest
from sandpiper.plan.application.create_todo import CreateNewToDoRequest
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

from . import __version__

# .envファイルから環境変数を読み込み
load_dotenv()

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
def create_project(
    name: str = typer.Argument(..., help="プロジェクト名"),
    start_date: str = typer.Option(..., help="開始日 (YYYY-MM-DD形式)"),
    end_date: str = typer.Option(None, help="終了日 (YYYY-MM-DD形式)"),
) -> None:
    """新しいプロジェクトを作成します"""
    from datetime import datetime

    from sandpiper.plan.application.create_project import CreateProjectRequest

    # 日付パース
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]エラー: 開始日の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
        raise typer.Exit(code=1)

    end_date_obj = None
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]エラー: 終了日の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
            raise typer.Exit(code=1)

    sandpiper_app.create_project.execute(
        CreateProjectRequest(
            name=name,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )
    )


@app.command()
def create_project_task(
    title: str,
    project_id: str = typer.Option(..., "--project-id", help="関連するプロジェクトのNotion ID"),
    status: str = typer.Option("TODO", help="ステータス (TODO, IN_PROGRESS, DONE)"),
) -> None:
    """新しいプロジェクトタスクを作成します"""
    try:
        status_enum = ToDoStatusEnum[status]
    except KeyError:
        console.print(f"[red]エラー: 無効なステータスです: {status}[/red]")
        console.print("[yellow]有効なステータス: TODO, IN_PROGRESS, DONE[/yellow]")
        raise typer.Exit(code=1)

    sandpiper_app.create_project_task.execute(
        request=CreateProjectTaskRequest(
            title=title,
            project_id=project_id,
            status=status_enum,
        )
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


@app.command()
def get_github_activity(
    date: str = typer.Option(None, help="対象日 (YYYY-MM-DD形式)"),
    username: str = typer.Option("koboriakira", help="GitHubユーザー名"),
    json: bool = typer.Option(False, "--json", help="JSON形式で出力する"),
    markdown: bool = typer.Option(False, "--markdown", help="Markdown形式で出力する"),
) -> None:
    """GitHubの活動ログを取得します"""
    import json as _json
    from datetime import datetime

    # 日付パース
    target_date = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            target_date = date_obj.replace(tzinfo=UTC)
        except ValueError:
            console.print("[red]エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
            raise typer.Exit(code=1)

    # GitHub活動ログ取得
    try:
        result = sandpiper_app.get_github_activity.execute(
            username=username,
            target_date=target_date,
        )
    except ValueError as e:
        console.print(f"[red]エラー: {e}[/red]")
        console.print("[yellow]GITHUB_TOKEN環境変数が設定されているか確認してください。[/yellow]")
        raise typer.Exit(code=1)

    # 出力
    if json:
        activity_dict = {
            "date": result.date,
            "username": result.username,
            "summary": {
                "total_events": result.summary.total_events,
                "commits_count": result.summary.commits_count,
                "pull_requests_count": result.summary.pull_requests_count,
                "issues_count": result.summary.issues_count,
                "reviews_count": result.summary.reviews_count,
            },
            "commits": [
                {
                    "sha": commit.sha,
                    "message": commit.message,
                    "repo": commit.repo,
                    "committed_at": commit.committed_at.isoformat(),
                }
                for commit in result.commits
            ],
            "pull_requests": [
                {
                    "number": pr.number,
                    "title": pr.title,
                    "action": pr.action,
                    "repo": pr.repo,
                    "created_at": pr.created_at.isoformat(),
                }
                for pr in result.pull_requests
            ],
            "issues": [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "action": issue.action,
                    "repo": issue.repo,
                    "created_at": issue.created_at.isoformat(),
                }
                for issue in result.issues
            ],
            "reviews": [
                {
                    "pr_number": review.pr_number,
                    "state": review.state,
                    "repo": review.repo,
                    "created_at": review.created_at.isoformat(),
                }
                for review in result.reviews
            ],
        }
        console.print(_json.dumps(activity_dict, ensure_ascii=False, indent=2))
    elif markdown:
        console.print(f"# GitHub Activity Log - {result.date}")
        console.print(f"**User:** {result.username}\n")
        console.print("## Summary")
        console.print(f"- Total Events: {result.summary.total_events}")
        console.print(f"- Commits: {result.summary.commits_count}")
        console.print(f"- Pull Requests: {result.summary.pull_requests_count}")
        console.print(f"- Issues: {result.summary.issues_count}")
        console.print(f"- Reviews: {result.summary.reviews_count}\n")

        if result.commits:
            console.print("## Commits")
            for commit in result.commits:
                console.print(f"- [{commit.repo}] `{commit.sha}`: {commit.message[:50]}")
            console.print()

        if result.pull_requests:
            console.print("## Pull Requests")
            for pr in result.pull_requests:
                console.print(f"- [{pr.repo}] #{pr.number}: {pr.title} ({pr.action})")
            console.print()

        if result.issues:
            console.print("## Issues")
            for issue in result.issues:
                console.print(f"- [{issue.repo}] #{issue.number}: {issue.title} ({issue.action})")
            console.print()

        if result.reviews:
            console.print("## Reviews")
            for review in result.reviews:
                console.print(f"- [{review.repo}] PR #{review.pr_number}: {review.state}")
            console.print()
    else:
        console.print(f"[bold cyan]📅 GitHub Activity Log - {result.date}[/bold cyan]")
        console.print(f"[bold]👤 User:[/bold] {result.username}\n")
        console.print("[bold green]📈 Summary:[/bold green]")
        console.print(f"  - Total Events: {result.summary.total_events}")
        console.print(f"  - Commits: {result.summary.commits_count}")
        console.print(f"  - Pull Requests: {result.summary.pull_requests_count}")
        console.print(f"  - Issues: {result.summary.issues_count}")
        console.print(f"  - Reviews: {result.summary.reviews_count}\n")

        if result.commits:
            console.print("[bold blue]💻 Commits:[/bold blue]")
            for commit in result.commits:
                console.print(f"  - [{commit.repo}] {commit.sha}: {commit.message[:50]}")
            console.print()

        if result.pull_requests:
            console.print("[bold magenta]🔀 Pull Requests:[/bold magenta]")
            for pr in result.pull_requests:
                console.print(f"  - [{pr.repo}] #{pr.number}: {pr.title} ({pr.action})")
            console.print()

        if result.issues:
            console.print("[bold yellow]🐛 Issues:[/bold yellow]")
            for issue in result.issues:
                console.print(f"  - [{issue.repo}] #{issue.number}: {issue.title} ({issue.action})")
            console.print()

        if result.reviews:
            console.print("[bold]👀 Reviews:[/bold]")
            for review in result.reviews:
                console.print(f"  - [{review.repo}] PR #{review.pr_number}: {review.state}")
            console.print()


if __name__ == "__main__":
    app()
