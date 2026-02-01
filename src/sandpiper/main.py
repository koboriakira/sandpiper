"""メインアプリケーション"""

from datetime import UTC

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from sandpiper.app.app import bootstrap
from sandpiper.plan.application.create_project_task import CreateProjectTaskRequest
from sandpiper.plan.application.create_someday_item import CreateSomedayItemRequest
from sandpiper.plan.application.create_todo import CreateNewToDoRequest
from sandpiper.plan.domain.someday_item import SomedayTiming
from sandpiper.plan.domain.todo import ToDoKind
from sandpiper.recipe.application.create_recipe import CreateRecipeRequest, IngredientRequest
from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
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
def create_todo(
    title: str,
    start: bool = typer.Option(False, help="タスクをすぐに開始するかどうか"),
    next_task: bool = typer.Option(False, "--next", help="差し込みタスクとして現在セクションに追加"),
) -> None:
    """新しいToDoタスクを作成します

    --next オプションを指定すると、差し込みタスクとして作成されます:
    - タスク種別: 差し込み
    - セクション: 現在時刻から判定
    - 並び順: 現在時刻(HH:mm形式)
    """
    if next_task:
        now = jst_now()
        current_section = TaskChuteSection.new(now)
        sort_order = now.strftime("%H:%M")
        console.print(f"[dim]差し込みタスク: セクション={current_section.value}, 並び順={sort_order}[/dim]")
        sandpiper_app.create_todo.execute(
            request=CreateNewToDoRequest(
                title=title,
                kind=ToDoKind.INTERRUPTION,
                section=current_section,
                sort_order=sort_order,
            ),
            enableStart=start,
        )
    else:
        sandpiper_app.create_todo.execute(
            request=CreateNewToDoRequest(
                title=title,
            ),
            enableStart=start,
        )


@app.command()
def create_todo_next_section(
    title: str = typer.Argument(..., help="ToDoのタイトル"),
    start: bool = typer.Option(False, help="タスクをすぐに開始するかどうか"),
) -> None:
    """現時刻の次のセクションに単発ToDoを作成します

    現在時刻に該当するセクションの次のセクションにタスクを追加します。
    例: 現在が10:00-13:00 (B) の場合、13:00-17:00 (C) にタスクが作成されます。
    """
    current_section = TaskChuteSection.new()
    next_section = current_section.next()
    console.print(f"[dim]現在のセクション: {current_section.value} → 次のセクション: {next_section.value}[/dim]")
    sandpiper_app.create_todo.execute(
        request=CreateNewToDoRequest(
            title=title,
            kind=ToDoKind.SINGLE,
            section=next_section,
        ),
        enableStart=start,
    )


@app.command()
def create_someday(
    title: str = typer.Argument(..., help="サムデイアイテムのタイトル"),
    timing: str = typer.Option(
        "明日",
        "--timing",
        "-t",
        help="タイミングを指定 (明日/いつか/ついでに)",
    ),
    do_tomorrow: bool = typer.Option(
        False,
        "--do-tomorrow",
        "-d",
        help="明日やるフラグを設定",
    ),
    context: str = typer.Option(
        None,
        "--context",
        "-c",
        help="コンテクストを指定 (カンマ区切りで複数指定可能: 外出,仕事)",
    ),
) -> None:
    """サムデイリストにアイテムを追加します

    デフォルトではタイミングが「明日」に設定されます。
    """
    # タイミングをEnum値に変換
    timing_map = {
        "明日": SomedayTiming.TOMORROW,
        "いつか": SomedayTiming.SOMEDAY,
        "ついでに": SomedayTiming.INCIDENTALLY,
    }
    timing_value = timing_map.get(timing)
    if timing_value is None:
        console.print(f"[red]エラー: 不正なタイミング値です: {timing}[/red]")
        console.print("[yellow]有効な値: 明日, いつか, ついでに[/yellow]")
        raise typer.Exit(1)

    # コンテクストをリストに変換
    context_list: list[str] = []
    if context:
        context_list = [c.strip() for c in context.split(",") if c.strip()]

    result = sandpiper_app.create_someday_item.execute(
        request=CreateSomedayItemRequest(
            title=title,
            timing=timing_value,
            do_tomorrow=do_tomorrow,
            context=context_list,
        ),
    )

    # 結果を表示
    output_parts = [f"サムデイアイテムを作成しました: {result.title}"]
    output_parts.append(f"タイミング: {result.timing}")
    if result.do_tomorrow:
        output_parts.append("明日やる: ✓")
    if result.context:
        output_parts.append(f"コンテクスト: {', '.join(result.context)}")
    console.print(f"[green]{' | '.join(output_parts)}[/green]")


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
def get_todo_log(
    date_filter: str = typer.Option(..., "--date", help="指定日付以降のログを取得 (YYYY-MM-DD形式)"),
    json: bool = typer.Option(False, "--json", help="JSON形式で出力する"),
    markdown: bool = typer.Option(False, "--markdown", help="Markdown形式で出力する"),
) -> None:
    """指定日付以降の完了タスクとカレンダー予定を時系列で取得します"""
    import json as _json
    from datetime import datetime as dt
    from typing import Any

    from sandpiper.review.query.activity_log_item import ActivityType

    try:
        target_date = dt.strptime(date_filter, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
        raise typer.Exit(code=1)

    result = sandpiper_app.get_todo_log.execute(target_date)

    if json:

        def item_to_dict(item: Any) -> dict[str, Any]:
            return {
                "type": item.activity_type.value,
                "title": item.title,
                "start_datetime": item.start_datetime.strftime("%Y-%m-%d %H:%M"),
                "end_datetime": item.end_datetime.strftime("%Y-%m-%d %H:%M"),
                "kind": item.kind if item.kind else None,
                "project_name": item.project_name if item.project_name else None,
                "category": item.category if item.category else None,
            }

        items_json = [item_to_dict(item) for item in result]
        console.print(_json.dumps(items_json, ensure_ascii=False, indent=2))
    elif markdown:
        lines = ["| 種類 | タイトル | 開始 | 終了 | 詳細 |", "| --- | --- | --- | --- | --- |"]
        for item in result:
            type_label = "TODO" if item.activity_type == ActivityType.TODO else "予定"
            title = item.title.replace("|", "\\|")
            start = item.start_datetime.strftime("%H:%M")
            end = item.end_datetime.strftime("%H:%M")
            if item.activity_type == ActivityType.TODO:
                detail = f"{item.kind}" + (f" / {item.project_name}" if item.project_name else "")
            else:
                detail = item.category if item.category else ""
            lines.append(f"| {type_label} | {title} | {start} | {end} | {detail} |")
        console.print("\n".join(lines))
    else:
        for item in result:
            if item.activity_type == ActivityType.TODO:
                prefix = f"【TODO {item.kind}】" + (f"[{item.project_name}] " if item.project_name else "")
            else:
                prefix = f"【予定 {item.category}】" if item.category else "【予定】"
            time_range = f" ({item.start_datetime.strftime('%H:%M')} - {item.end_datetime.strftime('%H:%M')})"
            console.print(f"- {prefix}{item.title}{time_range}")


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

    # 論理削除されたページを物理削除してからメイン処理を実行
    console.print("[dim]論理削除されたページをアーカイブ中...[/dim]")
    archive_result = sandpiper_app.archive_deleted_pages.execute()
    if archive_result.total_deleted_count > 0:
        console.print(f"[green]アーカイブ完了: {archive_result.total_deleted_count}件削除[/green]")

    sandpiper_app.create_repeat_task.execute(basis_date=date_obj)


@app.command()
def create_schedule_tasks(
    target_date: str = typer.Option(..., "--date", help="スケジュールタスクを作成する対象日 (YYYY-MM-DD形式)"),
) -> None:
    """カレンダーイベントからスケジュールタスクを作成します

    指定された日付のカレンダーイベントを取得し、
    それぞれをスケジュールタスクとしてTODOリストに登録します。

    - 実行時間: イベントの開始時刻と終了時刻から計算
    - 並び順: 開始時刻(HH:mm形式)
    - タスク種別: スケジュール
    """
    from datetime import datetime

    try:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
        raise typer.Exit(code=1)

    result = sandpiper_app.create_schedule_tasks.execute(target_date=date_obj)
    console.print(f"[green]スケジュールタスク作成完了: {result.created_count}件[/green]")


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


@app.command()
def search_jira_tickets(
    jql: str = typer.Option(None, help="JQLクエリ文字列"),
    project: str = typer.Option(None, help="プロジェクトキー"),
    issue_type: str = typer.Option(None, help="課題タイプ (複数の場合はカンマ区切り)"),
    status: str = typer.Option(None, help="ステータス (複数の場合はカンマ区切り)"),
    assignee: str = typer.Option(None, help="担当者 (currentUser() で自分)"),
    max_results: int = typer.Option(50, help="最大取得件数"),
    output_format: str = typer.Option("table", help="出力形式 (table, json)"),
) -> None:
    """JIRAのチケット情報を検索します"""
    import json

    from rich.table import Table

    from sandpiper.plan.query.jira_ticket_query import RestApiJiraTicketQuery

    try:
        query = RestApiJiraTicketQuery()
        tickets = query.search_tickets(
            jql=jql,
            project=project,
            issue_type=issue_type,
            status=status,
            assignee=assignee,
            max_results=max_results,
        )

        if not tickets:
            console.print("[yellow]チケットが見つかりませんでした[/yellow]")
            return

        if output_format.lower() == "json":
            # JSON出力
            tickets_data = [ticket.to_dict() for ticket in tickets]
            console.print_json(json.dumps(tickets_data, ensure_ascii=False, indent=2))
        else:
            # テーブル出力
            table = Table(title=f"JIRA Tickets ({len(tickets)} 件)")
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Summary", style="white")
            table.add_column("Type", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Assignee", style="blue")

            for ticket in tickets:
                table.add_row(
                    ticket.issue_key,
                    ticket.summary[:50] + "..." if len(ticket.summary) > 50 else ticket.summary,
                    ticket.issue_type,
                    ticket.status,
                    ticket.assignee or "未割当",
                )

            console.print(table)
            console.print(f"\n[bold]合計: {len(tickets)} 件[/bold]")

    except ValueError as e:
        console.print(f"[red]設定エラー: {e}[/red]")
        console.print("[yellow]BUSINESS_JIRA_USERNAME と BUSINESS_JIRA_API_TOKEN の環境変数を設定してください[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def get_jira_ticket(
    issue_key: str = typer.Argument(..., help="チケットキー (例: PROJ-123)"),
    output_format: str = typer.Option("detail", help="出力形式 (detail, json)"),
) -> None:
    """JIRAの個別チケット情報を取得します"""
    import json

    from rich.panel import Panel
    from rich.table import Table

    from sandpiper.plan.query.jira_ticket_query import RestApiJiraTicketQuery

    try:
        query = RestApiJiraTicketQuery()
        ticket = query.get_ticket(issue_key)

        if not ticket:
            console.print(f"[red]チケット {issue_key} が見つかりませんでした[/red]")
            raise typer.Exit(code=1)

        if output_format.lower() == "json":
            # JSON出力
            console.print_json(json.dumps(ticket.to_dict(), ensure_ascii=False, indent=2))
        else:
            # 詳細出力
            console.print(
                Panel(
                    f"[bold]{ticket.summary}[/bold]",
                    title=f"[cyan]{ticket.issue_key}[/cyan]",
                    border_style="blue",
                )
            )

            # 基本情報テーブル
            info_table = Table(show_header=False, box=None, padding=(0, 1))
            info_table.add_column("Field", style="bold")
            info_table.add_column("Value")

            info_table.add_row("タイプ:", ticket.issue_type)
            info_table.add_row("ステータス:", ticket.status)
            if ticket.priority:
                info_table.add_row("優先度:", ticket.priority)
            if ticket.assignee:
                info_table.add_row("担当者:", ticket.assignee)
            if ticket.reporter:
                info_table.add_row("起票者:", ticket.reporter)
            if ticket.created:
                info_table.add_row("作成日:", ticket.created.strftime("%Y-%m-%d %H:%M"))
            if ticket.updated:
                info_table.add_row("更新日:", ticket.updated.strftime("%Y-%m-%d %H:%M"))
            if ticket.due_date:
                info_table.add_row("期限:", ticket.due_date.strftime("%Y-%m-%d"))
            if ticket.story_points:
                info_table.add_row("ストーリーポイント:", str(ticket.story_points))
            if ticket.sprint:
                info_table.add_row("スプリント:", ticket.sprint)

            console.print(info_table)

            # 説明
            if ticket.description:
                console.print(
                    Panel(
                        ticket.description[:500] + "..." if len(ticket.description) > 500 else ticket.description,
                        title="説明",
                        border_style="green",
                    )
                )

            # ラベル・フィックスバージョン
            if ticket.labels:
                console.print(f"[bold]ラベル:[/bold] {', '.join(ticket.labels)}")
            if ticket.fix_versions:
                console.print(f"[bold]フィックスバージョン:[/bold] {', '.join(ticket.fix_versions)}")

            # URL
            if ticket.url:
                console.print(f"[bold blue]URL:[/bold blue] {ticket.url}")

    except ValueError as e:
        console.print(f"[red]設定エラー: {e}[/red]")
        console.print("[yellow]BUSINESS_JIRA_USERNAME と BUSINESS_JIRA_API_TOKEN の環境変数を設定してください[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def create_notion_pages(
    file_path: str = typer.Argument(..., help="JSONファイルのパス"),
) -> None:
    """JSONファイルからNotionページを作成します(現在はRecipeのみ対応)"""
    import json
    from pathlib import Path

    json_path = Path(file_path)

    # ファイル存在チェック
    if not json_path.exists():
        console.print(f"[red]エラー: ファイルが見つかりません: {file_path}[/red]")
        raise typer.Exit(code=1)

    # JSONファイル読み込み
    try:
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]エラー: JSONファイルの解析に失敗しました: {e}[/red]")
        raise typer.Exit(code=1)

    # データが配列であることを確認
    if not isinstance(data, list):
        console.print("[red]エラー: JSONファイルは配列形式である必要があります[/red]")
        raise typer.Exit(code=1)

    # 各アイテムを処理
    created_count = 0
    skipped_count = 0

    for item in data:
        item_type = item.get("type", "").lower()

        if item_type == "recipe":
            try:
                # IngredientRequestリストを作成
                ingredients = [
                    IngredientRequest(
                        name=ing.get("name", ""),
                        quantity=ing.get("quantity", ""),
                    )
                    for ing in item.get("ingredients", [])
                ]

                # CreateRecipeRequestを作成
                request = CreateRecipeRequest(
                    title=item.get("title", ""),
                    reference_url=item.get("reference_url"),
                    ingredients=ingredients,
                    steps=item.get("steps", []),
                )

                # レシピを作成
                result = sandpiper_app.create_recipe.execute(request)
                console.print(f"[green]作成完了: {result.title} (ID: {result.id})[/green]")
                created_count += 1

            except Exception as e:
                console.print(f"[red]エラー: レシピ '{item.get('title', '不明')}' の作成に失敗しました: {e}[/red]")
        else:
            console.print(f"[yellow]スキップ: 未対応のタイプ '{item.get('type', '不明')}'[/yellow]")
            skipped_count += 1

    # 結果サマリー
    console.print(f"\n[bold]処理完了: {created_count}件作成, {skipped_count}件スキップ[/bold]")


@app.command()
def sync_jira_to_project(
    jira_project: str = typer.Option("SU", "--project", "-p", help="JIRAプロジェクトキー"),
) -> None:
    """JIRAチケットをNotionプロジェクトに同期します

    SUプロジェクトの自分にアサインされたTask/Story/Bugチケットを取得し、
    Notionプロジェクトデータベースに追加します。

    - ステータスが"To Do"または"In Progress"のチケットを対象
    - 既にJira URLが登録されているプロジェクトは作成しない(重複チェック)
    - プロジェクト作成時に同名のプロジェクトタスクも作成
    """
    console.print(f"[bold]JIRAチケットをNotionプロジェクトに同期中...[/bold] (プロジェクト: {jira_project})")

    try:
        result = sandpiper_app.sync_jira_to_project.execute(jira_project=jira_project)

        # 作成されたプロジェクト
        if result.created_projects:
            console.print(f"\n[green][bold]作成されたプロジェクト ({len(result.created_projects)}件):[/bold][/green]")
            for project in result.created_projects:
                console.print(f"  - {project.name}")
                if project.jira_url:
                    console.print(f"    [blue]{project.jira_url}[/blue]")

        # スキップされたチケット
        if result.skipped_tickets:
            console.print(f"\n[yellow][bold]スキップされたチケット ({len(result.skipped_tickets)}件):[/bold][/yellow]")
            for ticket in result.skipped_tickets:
                console.print(f"  - {ticket.issue_key}: {ticket.summary}")

        # Notionにのみ存在するプロジェクト (JIRA側で完了済み等)
        if result.notion_only_projects:
            console.print(f"\n[magenta][bold]Notionのみに存在 ({len(result.notion_only_projects)}件):[/bold][/magenta]")
            console.print("[dim]※JIRA側で完了済みまたはステータス変更の可能性があります[/dim]")
            for project in result.notion_only_projects:
                console.print(f"  - {project.name}")
                if project.jira_url:
                    console.print(f"    [blue]{project.jira_url}[/blue]")

        # サマリー
        console.print(
            f"\n[bold]同期完了: {len(result.created_projects)}件作成, "
            f"{len(result.skipped_tickets)}件スキップ, "
            f"{len(result.notion_only_projects)}件Notionのみ[/bold]"
        )

    except ValueError as e:
        console.print(f"[red]設定エラー: {e}[/red]")
        console.print("[yellow]BUSINESS_JIRA_USERNAME と BUSINESS_JIRA_API_TOKEN の環境変数を設定してください[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def create_tasks_from_someday(
    dry_run: bool = typer.Option(False, "--dry-run", help="実際に作成せず対象のみ表示"),
) -> None:
    """サムデイリストの「明日やる」からTODOを作成します

    「明日やる」にチェックが入っているサムデイリストのアイテムを
    TODOとして作成し、元のサムデイリストから削除します。
    """
    if dry_run:
        console.print("[dim]ドライラン: 「明日やる」のサムデイアイテムを検索中...[/dim]")
        # 注: dry_runはアプリケーション層でサポートされていないため、
        # 実際の実行結果を表示するが、本番ではコメントを残す
        console.print("[yellow]現在ドライランモードは未対応です。--dry-runオプションなしで実行してください。[/yellow]")
        return

    console.print("[bold]サムデイリストからTODOを作成中...[/bold]")
    result = sandpiper_app.create_tasks_by_someday_list.execute()

    if result.created_count == 0:
        console.print("[yellow]「明日やる」のサムデイアイテムはありませんでした[/yellow]")
    else:
        console.print(f"[green][bold]TODO作成完了: {result.created_count}件[/bold][/green]")
        for title in result.created_titles:
            console.print(f"  - {title}")


@app.command()
def archive_old_todos(
    days: int = typer.Option(7, help="完了してからの経過日数 (デフォルト: 7日)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="実際にアーカイブせず対象のみ表示"),
) -> None:
    """完了して指定日数経過したTODOをアーカイブします

    DONEステータスで完了日時から指定日数経過したタスクを
    アーカイブ用のデータベースに移動し、元のデータベースから削除します。
    """
    from sandpiper.shared.infrastructure.archive_old_todos import ArchiveOldTodos

    if dry_run:
        console.print(f"[dim]ドライラン: {days}日以上前に完了したTODOを検索中...[/dim]")
        archive_service = ArchiveOldTodos(archive_days=days)
        result = archive_service.execute(dry_run=True)
        if result.archived_count == 0:
            console.print("[yellow]アーカイブ対象のTODOはありません[/yellow]")
        else:
            console.print(f"[bold]アーカイブ対象: {result.archived_count}件[/bold]")
            for title in result.archived_titles:
                console.print(f"  - {title}")
        console.print("[dim](ドライランのため実際のアーカイブは行われていません)[/dim]")
        return

    console.print(f"[bold]完了して{days}日以上経過したTODOをアーカイブ中...[/bold]")
    archive_service = ArchiveOldTodos(archive_days=days)
    result = archive_service.execute()

    if result.archived_count == 0:
        console.print("[yellow]アーカイブ対象のTODOはありませんでした[/yellow]")
    else:
        console.print(f"[green][bold]アーカイブ完了: {result.archived_count}件[/bold][/green]")
        for title in result.archived_titles:
            console.print(f"  - {title}")


if __name__ == "__main__":
    app()
