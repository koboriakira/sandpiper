"""メインアプリケーション"""

from datetime import UTC

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from sandpiper.app.app import bootstrap
from sandpiper.clips.application.create_clip import CreateClipRequest
from sandpiper.plan.application.create_project_task import CreateProjectTaskRequest
from sandpiper.plan.application.create_someday_item import CreateSomedayItemRequest
from sandpiper.plan.application.create_todo import CreateNewToDoRequest
from sandpiper.plan.domain.someday_item import SomedayTiming
from sandpiper.recipe.application.create_recipe import CreateRecipeRequest, IngredientRequest
from sandpiper.shared.infrastructure.cron_notifier import CronNotifier
from sandpiper.shared.infrastructure.slack_notice_messanger import SlackNoticeMessanger
from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_kind import ToDoKind
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

from . import __version__

# .envファイルから環境変数を読み込み
load_dotenv()

# デフォルトSlackチャンネルID
_DEFAULT_SLACK_CHANNEL_ID = "C0AJQR86PK9"


def _create_notifier() -> CronNotifier:
    """cron通知用のCronNotifierインスタンスを生成する"""
    messanger = SlackNoticeMessanger(channel_id=_DEFAULT_SLACK_CHANNEL_ID)
    return CronNotifier(messanger=messanger)


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
def prepare_tomorrow_todos() -> None:
    """明日(または今日)のTODOリストを一括作成します

    ルーチンタスク、プロジェクトタスク、サムデイリスト、カレンダーイベントから
    TODOを自動生成します。

    日本時間18:00〜23:59は「明日」、00:00〜17:59は「今日」として扱います。
    cronから定期実行する用途を想定しています。
    """
    from sandpiper.plan.application.prepare_tomorrow_todos import PrepareTomorrowTodos

    now = jst_now()
    is_tomorrow, basis_date = PrepareTomorrowTodos.resolve_params_from_now(now_hour=now.hour, today=now.date())

    target_label = "明日" if is_tomorrow else "今日"
    console.print(f"[bold]{target_label}のTODOリストを作成中...[/bold] (基準日: {basis_date})")

    result = sandpiper_app.prepare_tomorrow_todos.execute(is_tomorrow=is_tomorrow, basis_date=basis_date)

    console.print(f"[green][bold]{result.summary}[/bold][/green]")


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
    notify: bool = typer.Option(False, "--notify", help="実行結果をSlackに通知する (cron実行用)"),
) -> None:
    """JIRAチケットをNotionプロジェクトに同期します

    SUプロジェクトの自分にアサインされたTask/Story/Bugチケットを取得し、
    Notionプロジェクトデータベースに追加します。

    - ステータスが"To Do"または"In Progress"のチケットを対象
    - 既にJira URLが登録されているプロジェクトは作成しない(重複チェック)
    - プロジェクト作成時に同名のプロジェクトタスクも作成
    """
    console.print(f"[bold]JIRAチケットをNotionプロジェクトに同期中...[/bold] (プロジェクト: {jira_project})")

    notifier = _create_notifier() if notify else None

    try:
        result = sandpiper_app.sync_jira_to_project.execute(jira_project=jira_project)

        # 作成されたプロジェクト
        if result.created_projects:
            console.print(f"\n[green][bold]作成されたプロジェクト ({len(result.created_projects)}件):[/bold][/green]")
            for project in result.created_projects:
                console.print(f"  - {project.name}")
                if project.jira_url:
                    console.print(f"    [blue]{project.jira_url}[/blue]")

        # Jira完了によりDoneに更新されたプロジェクト
        if result.completed_projects:
            console.print(f"\n[cyan][bold]完了に更新 ({len(result.completed_projects)}件):[/bold][/cyan]")
            for project in result.completed_projects:
                console.print(f"  - {project.name}")
                if project.jira_url:
                    console.print(f"    [blue]{project.jira_url}[/blue]")

        # スキップされたチケット
        if result.skipped_tickets:
            console.print(f"\n[yellow][bold]スキップされたチケット ({len(result.skipped_tickets)}件):[/bold][/yellow]")
            for ticket in result.skipped_tickets:
                console.print(f"  - {ticket.issue_key}: {ticket.summary}")

        # Notionにのみ存在するプロジェクト (JIRA側でステータス変更等)
        if result.notion_only_projects:
            console.print(f"\n[magenta][bold]Notionのみに存在 ({len(result.notion_only_projects)}件):[/bold][/magenta]")
            console.print("[dim]※JIRA側でステータス変更の可能性があります[/dim]")
            for project in result.notion_only_projects:
                console.print(f"  - {project.name}")
                if project.jira_url:
                    console.print(f"    [blue]{project.jira_url}[/blue]")

        # サマリー
        summary = (
            f"{len(result.created_projects)}件作成, "
            f"{len(result.completed_projects)}件完了, "
            f"{len(result.skipped_tickets)}件スキップ, "
            f"{len(result.notion_only_projects)}件Notionのみ"
        )
        console.print(f"\n[bold]同期完了: {summary}[/bold]")

        if notifier:
            notifier.notify_success(command="sync-jira-to-project", summary=summary)

    except ValueError as e:
        console.print(f"[red]設定エラー: {e}[/red]")
        console.print("[yellow]BUSINESS_JIRA_USERNAME と BUSINESS_JIRA_API_TOKEN の環境変数を設定してください[/yellow]")
        if notifier:
            notifier.notify_failure(command="sync-jira-to-project", error=str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        if notifier:
            notifier.notify_failure(command="sync-jira-to-project", error=str(e))
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
    days: int = typer.Option(1, help="閾値日数: 本日0時からN-1日前が閾値 (デフォルト: 1=前日以前)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="実際にアーカイブせず対象のみ表示"),
    notify: bool = typer.Option(False, "--notify", help="実行結果をSlackに通知する (cron実行用)"),
) -> None:
    """完了したTODOをアーカイブ/削除します

    DONEステータスで前日以前に完了したタスクを処理します。
    - リピート(ルーティン)種別: アーカイブせず削除のみ
    - それ以外: アーカイブ用データベースに移動後、元のデータベースから削除
    """
    from sandpiper.shared.infrastructure.archive_old_todos import ArchiveOldTodos

    if dry_run:
        console.print(f"[dim]ドライラン: {days}日閾値で完了したTODOを検索中...[/dim]")
        archive_service = ArchiveOldTodos(archive_days=days)
        result = archive_service.execute(dry_run=True)
        total = result.archived_count + result.deleted_routine_count
        if total == 0:
            console.print("[yellow]処理対象のTODOはありません[/yellow]")
        else:
            if result.archived_count > 0:
                console.print(f"[bold]アーカイブ対象: {result.archived_count}件[/bold]")
                for title in result.archived_titles:
                    console.print(f"  - {title}")
            if result.deleted_routine_count > 0:
                console.print(f"[bold]削除対象(ルーティン): {result.deleted_routine_count}件[/bold]")
                for title in result.deleted_routine_titles:
                    console.print(f"  - {title}")
        console.print("[dim](ドライランのため実際の処理は行われていません)[/dim]")
        return

    notifier = _create_notifier() if notify else None

    try:
        console.print("[bold]前日以前に完了したTODOを処理中...[/bold]")
        archive_service = ArchiveOldTodos(archive_days=days)
        result = archive_service.execute()

        summary = f"アーカイブ{result.archived_count}件、ルーティン削除{result.deleted_routine_count}件"
        if result.archived_count == 0 and result.deleted_routine_count == 0:
            console.print("[yellow]処理対象のTODOはありませんでした[/yellow]")
        else:
            if result.archived_count > 0:
                console.print(f"[green][bold]アーカイブ完了: {result.archived_count}件[/bold][/green]")
                for title in result.archived_titles:
                    console.print(f"  - {title}")
            if result.deleted_routine_count > 0:
                console.print(f"[green][bold]ルーティン削除: {result.deleted_routine_count}件[/bold][/green]")
                for title in result.deleted_routine_titles:
                    console.print(f"  - {title}")

        if notifier:
            notifier.notify_success(command="archive-old-todos", summary=summary)

    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        if notifier:
            notifier.notify_failure(command="archive-old-todos", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def create_clip(
    url: str = typer.Argument(..., help="クリップするURLを指定"),
    title: str = typer.Option(None, "--title", "-t", help="タイトルを指定 (省略時はURLから自動取得)"),
) -> None:
    """URLからWebクリップを作成してNotionに保存します

    URLを指定してClipsデータベースにWebクリップを作成します。
    タイトルを省略した場合、ページのタイトルを自動取得します。
    YouTube URLの場合はYouTube APIからタイトルを取得します。
    """
    try:
        request = CreateClipRequest(url=url, title=title)
        result = sandpiper_app.create_clip.execute(request)
        console.print(f"[green]Clipを作成しました: {result.title}[/green]")
        console.print(f"  URL: {result.url}")
        console.print(f"  タイプ: {result.inbox_type.value}")
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def override_section_by_schedule(
    page_id: str = typer.Argument(None, help="TODOのNotion ページID (省略時はステータスがTODOのすべてのタスクを処理)"),
) -> None:
    """TODOの予定開始時刻からセクションを上書きします

    指定されたTODOの「予定」プロパティの開始時刻を取得し、
    その時刻に基づいてセクションプロパティを上書きします。

    - page_idを省略した場合、ステータスがTODOのすべてのタスクを対象とします
    - 予定開始時刻が設定されていない場合はスキップされます (単体実行時はエラー)
    - セクションは時刻に応じて自動計算されます (A_07_10, B_10_13, etc.)
    """
    try:
        if page_id:
            # 単体実行
            result = sandpiper_app.override_section_by_schedule.execute(page_id=page_id)
            old_section_str = result.old_section.value if result.old_section else "なし"
            console.print("[green][bold]セクション上書き完了[/bold][/green]")
            console.print(f"  タイトル: {result.title}")
            console.print(f"  予定開始: {result.scheduled_start_datetime_str}")
            console.print(f"  セクション: {old_section_str} → {result.new_section.value}")
        else:
            # 一括実行
            console.print("[dim]ステータスがTODOのすべてのタスクを処理中...[/dim]")
            bulk_result = sandpiper_app.override_section_by_schedule.execute_all()
            console.print(f"[green][bold]セクション上書き完了: {bulk_result.success_count}件[/bold][/green]")
            if bulk_result.skipped_count > 0:
                console.print(f"[yellow]スキップ: {bulk_result.skipped_count}件 (予定開始時刻なし)[/yellow]")
            for result in bulk_result.results:
                old_section_str = result.old_section.value if result.old_section else "なし"
                console.print(f"  - {result.title}: {old_section_str} → {result.new_section.value}")
    except ValueError as e:
        console.print(f"[red]エラー: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def list_unprocessed_clips() -> None:
    """未処理のWebクリップ一覧を表示します

    Notionに保存された未処理(unprocessed=True)のClipsを取得し、
    タイトルとURLを一覧で表示します。
    未読の記事やWebクリップを確認する用途を想定しています。
    """
    clips = sandpiper_app.list_unprocessed_clips.execute()

    if not clips:
        console.print("[yellow]未処理のClipはありません[/yellow]")
        return

    console.print(f"[bold]未処理のClip: {len(clips)}件[/bold]\n")
    for clip in clips:
        console.print(f"  [cyan]{clip.title}[/cyan]")
        console.print(f"    {clip.url}")


@app.command()
def cleanup_project_tasks(
    notify: bool = typer.Option(False, "--notify", help="実行結果をSlackに通知する (cron実行用)"),
) -> None:
    """親プロジェクトが完了・削除済みのプロジェクトタスクを整理します

    Done以外のプロジェクトタスクを全取得し:
    - 親プロジェクトがDone → タスクもDoneに更新
    - 親プロジェクトが存在しない → タスクをアーカイブ(削除)
    - それ以外 → スキップ
    """
    notifier = _create_notifier() if notify else None

    try:
        console.print("[bold]プロジェクトタスクを整理中...[/bold]")
        result = sandpiper_app.cleanup_project_tasks.execute()

        if result.completed_count > 0:
            console.print(f"[green][bold]完了に更新: {result.completed_count}件[/bold][/green]")
            for title in result.completed_titles:
                console.print(f"  - {title}")

        if result.deleted_count > 0:
            console.print(f"[yellow][bold]削除: {result.deleted_count}件[/bold][/yellow]")
            for title in result.deleted_titles:
                console.print(f"  - {title}")

        if result.completed_count == 0 and result.deleted_count == 0:
            console.print("[dim]整理対象のプロジェクトタスクはありませんでした[/dim]")

        if notifier:
            notifier.notify_success(command="cleanup-project-tasks", summary=result.summary)

    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        if notifier:
            notifier.notify_failure(command="cleanup-project-tasks", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def export_donelist(
    date_filter: str = typer.Option(..., "--date", help="対象日付 (YYYY-MM-DD形式)"),
    notify: bool = typer.Option(False, "--notify", help="実行結果をSlackに通知する (cron実行用)"),
) -> None:
    """完了タスクとカレンダー予定をObsidian DailyNoteに書き出します

    get-todo-logと同じデータを取得し、Obsidian Vaultの
    dailynote/YYYY/MM/DD/donelist.md に上書き出力します。
    """
    from datetime import datetime as dt
    from pathlib import Path

    from sandpiper.review.query.activity_log_item import ActivityType

    try:
        target_date = dt.strptime(date_filter, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
        raise typer.Exit(code=1)

    _DONELIST_SLACK_CHANNEL_ID = "C0AJQR86PK9"
    notifier = CronNotifier(messanger=SlackNoticeMessanger(channel_id=_DONELIST_SLACK_CHANNEL_ID)) if notify else None

    try:
        result = sandpiper_app.get_todo_log.execute(target_date)

        # 通常テキスト形式で行を生成
        lines: list[str] = []
        for item in result:
            if item.activity_type == ActivityType.TODO:
                prefix = f"【TODO {item.kind}】" + (f"[{item.project_name}] " if item.project_name else "")
            else:
                prefix = f"【予定 {item.category}】" if item.category else "【予定】"
            time_range = f" ({item.start_datetime.strftime('%H:%M')} - {item.end_datetime.strftime('%H:%M')})"
            lines.append(f"- {prefix}{item.title}{time_range}")

        content = "\n".join(lines) + "\n" if lines else ""

        # Obsidian Vault に書き出し
        vault_path = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/my-vault"
        output_path = vault_path / "dailynote" / f"{target_date:%Y/%m/%d}" / "donelist.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        summary = f"{len(lines)}件を {output_path} に出力"
        console.print(f"[green]{summary}[/green]")

        # Slack通知
        slack_messanger = SlackNoticeMessanger(channel_id=_DONELIST_SLACK_CHANNEL_ID)
        slack_messanger.send(f"[export-donelist] {date_filter}: {len(lines)}件出力しました")

        if notifier:
            notifier.notify_success(command="export-donelist", summary=summary)

    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")
        if notifier:
            notifier.notify_failure(command="export-donelist", error=str(e))
        raise typer.Exit(code=1)


@app.command()
def check_dakoku(
    notify: bool = typer.Option(False, "--notify", help="未完了時にSlackに通知する (cron実行用)"),
) -> None:
    """「打刻」TODOが未完了かチェックします

    ステータスがTODOまたはIN_PROGRESSのタスクの中に
    タイトルに「打刻」を含むものがあればSlack通知します。
    平日朝のcronで定期実行する用途を想定しています。
    """
    from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository

    repo = NotionTodoRepository()
    incomplete_todos: list[str] = []
    for status in [ToDoStatusEnum.TODO, ToDoStatusEnum.IN_PROGRESS]:
        todos = repo.find_by_status(status)
        incomplete_todos.extend(todo.title for todo in todos if "打刻" in todo.title)

    if not incomplete_todos:
        console.print("[green]打刻は完了済みです[/green]")
        return

    message = f"打刻が未完了です: {', '.join(incomplete_todos)}"
    console.print(f"[red][bold]{message}[/bold][/red]")

    if notify:
        notifier = _create_notifier()
        notifier.notify_success(command="check-dakoku", summary=message)


# ---------------------------------------------------------------------------
# Sub-apps: project / project-task / todo
# ---------------------------------------------------------------------------
# これらのコマンドはAIエージェントがNotionのプロパティを取得・更新する用途を想定。
# 出力はすべてJSON形式(stdout)とし、機械的に扱いやすくする。

_project_app = typer.Typer(help="プロジェクトのプロパティを取得・更新します")
_project_task_app = typer.Typer(help="プロジェクトタスクのプロパティを取得・更新します")
_todo_app = typer.Typer(help="TODOのプロパティを取得・更新します")
_page_app = typer.Typer(help="Notionページの取得")

app.add_typer(_project_app, name="project")
app.add_typer(_project_task_app, name="project-task")
app.add_typer(_todo_app, name="todo")
app.add_typer(_page_app, name="page")


# --- project ---


@_project_app.command("get")
def project_get(
    page_id: str = typer.Argument(..., help="プロジェクトのNotionページID"),
) -> None:
    """プロジェクトのプロパティをJSON形式で取得します"""
    import json as _json

    from sandpiper.plan.infrastructure.notion_project_repository import NotionProjectRepository

    repo = NotionProjectRepository()
    p = repo.find_as_inserted(page_id)
    print(
        _json.dumps(
            {
                "id": p.id,
                "name": p.name,
                "status": p.status.value if p.status else None,
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat() if p.end_date else None,
                "jira_url": p.jira_url,
                "claude_url": p.claude_url,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@_project_app.command("list")
def project_list(
    status: str = typer.Option(None, "--status", help="ステータスフィルター (TODO/IN_PROGRESS/DONE)"),
) -> None:
    """プロジェクト一覧をJSON形式で取得します"""
    import json as _json

    from sandpiper.plan.infrastructure.notion_project_repository import NotionProjectRepository

    repo = NotionProjectRepository()
    projects = repo.fetch_all()

    if status:
        try:
            status_enum = ToDoStatusEnum[status]
        except KeyError:
            console.print(f"[red]エラー: 無効なステータスです: {status}[/red]")
            console.print("[yellow]有効な値: TODO, IN_PROGRESS, DONE[/yellow]")
            raise typer.Exit(code=1)
        projects = [p for p in projects if p.status is not None and p.status.value == status_enum.value]

    print(
        _json.dumps(
            [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status.value if p.status else None,
                    "start_date": p.start_date.isoformat(),
                    "end_date": p.end_date.isoformat() if p.end_date else None,
                    "jira_url": p.jira_url,
                    "claude_url": p.claude_url,
                }
                for p in projects
            ],
            ensure_ascii=False,
            indent=2,
        )
    )


@_project_app.command("update")
def project_update(
    page_id: str = typer.Argument(..., help="プロジェクトのNotionページID"),
    status: str = typer.Option(None, "--status", help="新しいステータス (TODO/IN_PROGRESS/DONE)"),
    name: str = typer.Option(None, "--name", help="新しいプロジェクト名"),
    end_date: str = typer.Option(None, "--end-date", help="新しい完了日 (YYYY-MM-DD形式)"),
) -> None:
    """プロジェクトのプロパティを更新します"""
    from datetime import datetime

    from sandpiper.plan.infrastructure.notion_project_repository import NotionProjectRepository

    if not any([status, name, end_date]):
        console.print("[red]エラー: 更新するプロパティを指定してください (--status / --name / --end-date)[/red]")
        raise typer.Exit(code=1)

    repo = NotionProjectRepository()

    if status:
        try:
            status_enum = ToDoStatusEnum[status]
        except KeyError:
            console.print(f"[red]エラー: 無効なステータスです: {status}[/red]")
            raise typer.Exit(code=1)
        repo.update_status(page_id, status_enum)

    if name:
        repo.update_name(page_id, name)

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。[/red]")
            raise typer.Exit(code=1)
        repo.update_end_date(page_id, end_date_obj)

    console.print(f"[green]更新しました: {page_id}[/green]")


# --- project-task ---


@_project_task_app.command("get")
def project_task_get(
    page_id: str = typer.Argument(..., help="プロジェクトタスクのNotionページID"),
) -> None:
    """プロジェクトタスクのプロパティをJSON形式で取得します"""
    import json as _json

    from sandpiper.plan.infrastructure.notion_project_task_repository import NotionProjectTaskRepository

    repo = NotionProjectTaskRepository()
    t = repo.find(page_id)
    print(
        _json.dumps(
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "project_id": t.project_id,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@_project_task_app.command("list")
def project_task_list(
    project_id: str = typer.Option(None, "--project-id", help="プロジェクトIDフィルター"),
    status: str = typer.Option(None, "--status", help="ステータスフィルター (TODO/IN_PROGRESS/DONE)"),
) -> None:
    """プロジェクトタスク一覧をJSON形式で取得します"""
    import json as _json

    from sandpiper.plan.infrastructure.notion_project_task_repository import NotionProjectTaskRepository

    repo = NotionProjectTaskRepository()
    tasks = repo.fetch_all()

    if project_id:
        tasks = [t for t in tasks if t.project_id == project_id]

    if status:
        try:
            status_enum = ToDoStatusEnum[status]
        except KeyError:
            console.print(f"[red]エラー: 無効なステータスです: {status}[/red]")
            console.print("[yellow]有効な値: TODO, IN_PROGRESS, DONE[/yellow]")
            raise typer.Exit(code=1)
        tasks = [t for t in tasks if t.status.value == status_enum.value]

    print(
        _json.dumps(
            [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status.value,
                    "project_id": t.project_id,
                }
                for t in tasks
            ],
            ensure_ascii=False,
            indent=2,
        )
    )


@_project_task_app.command("update")
def project_task_update(
    page_id: str = typer.Argument(..., help="プロジェクトタスクのNotionページID"),
    status: str = typer.Option(None, "--status", help="新しいステータス (TODO/IN_PROGRESS/DONE)"),
    title: str = typer.Option(None, "--title", help="新しいタイトル"),
) -> None:
    """プロジェクトタスクのプロパティを更新します"""
    from sandpiper.plan.infrastructure.notion_project_task_repository import NotionProjectTaskRepository

    if not any([status, title]):
        console.print("[red]エラー: 更新するプロパティを指定してください (--status / --title)[/red]")
        raise typer.Exit(code=1)

    repo = NotionProjectTaskRepository()

    if status:
        try:
            status_enum = ToDoStatusEnum[status]
        except KeyError:
            console.print(f"[red]エラー: 無効なステータスです: {status}[/red]")
            raise typer.Exit(code=1)
        repo.update_status(page_id, status_enum)

    if title:
        repo.update_title(page_id, title)

    console.print(f"[green]更新しました: {page_id}[/green]")


# --- todo ---


@_todo_app.command("get")
def todo_get(
    page_id: str = typer.Argument(..., help="TODOのNotionページID"),
) -> None:
    """TODOのプロパティをJSON形式で取得します"""
    import json as _json

    from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository as PerformRepo

    repo = PerformRepo()
    t = repo.find(page_id)
    print(
        _json.dumps(
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "section": t.section.value if t.section else None,
                "scheduled_start": t.scheduled_start_datetime.isoformat() if t.scheduled_start_datetime else None,
                "scheduled_end": t.scheduled_end_datetime.isoformat() if t.scheduled_end_datetime else None,
                "project_task_id": t.project_task_page_id,
                "contexts": [c.value for c in t.contexts],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@_todo_app.command("list")
def todo_list(
    status: str = typer.Option(
        None, "--status", help="ステータスフィルター (TODO/IN_PROGRESS/DONE/ALL, デフォルト: TODO)"
    ),
) -> None:
    """TODO一覧をJSON形式で取得します (デフォルト: ステータスがTODOのもの)"""
    import json as _json

    from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository as PerformRepo

    repo = PerformRepo()

    if status is None or status == "TODO":
        todos = repo.find_by_status(ToDoStatusEnum.TODO)
    elif status == "ALL":
        todos = repo.fetch_all()
    else:
        try:
            status_enum = ToDoStatusEnum[status]
        except KeyError:
            console.print(f"[red]エラー: 無効なステータスです: {status}[/red]")
            console.print("[yellow]有効な値: TODO, IN_PROGRESS, DONE, ALL[/yellow]")
            raise typer.Exit(code=1)
        todos = repo.find_by_status(status_enum)

    print(
        _json.dumps(
            [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status.value,
                    "kind": t.kind.value if t.kind else None,
                    "section": t.section.value if t.section else None,
                    "scheduled_start": t.scheduled_start_datetime.isoformat() if t.scheduled_start_datetime else None,
                    "scheduled_end": t.scheduled_end_datetime.isoformat() if t.scheduled_end_datetime else None,
                    "project_task_id": t.project_task_page_id,
                    "contexts": [c.value for c in t.contexts],
                }
                for t in todos
            ],
            ensure_ascii=False,
            indent=2,
        )
    )


@_todo_app.command("update")
def todo_update(
    page_id: str = typer.Argument(..., help="TODOのNotionページID"),
    status: str = typer.Option(None, "--status", help="新しいステータス (TODO/IN_PROGRESS/DONE)"),
    section: str = typer.Option(
        None, "--section", help="新しいセクション (A_07_10/B_10_13/C_13_17/D_17_19/E_19_22/F_22_24/G_24_07)"
    ),
    title: str = typer.Option(None, "--title", help="新しいタイトル"),
) -> None:
    """TODOのプロパティを更新します"""
    from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository as PerformRepo

    if not any([status, section, title]):
        console.print("[red]エラー: 更新するプロパティを指定してください (--status / --section / --title)[/red]")
        raise typer.Exit(code=1)

    repo = PerformRepo()

    if status:
        try:
            status_enum = ToDoStatusEnum[status]
        except KeyError:
            console.print(f"[red]エラー: 無効なステータスです: {status}[/red]")
            raise typer.Exit(code=1)
        repo.update_status(page_id, status_enum)

    if section:
        try:
            section_enum = TaskChuteSection[section]
        except KeyError:
            console.print(f"[red]エラー: 無効なセクションです: {section}[/red]")
            console.print("[yellow]有効な値: A_07_10, B_10_13, C_13_17, D_17_19, E_19_22, F_22_24, G_24_07[/yellow]")
            raise typer.Exit(code=1)
        repo.update_section(page_id, section_enum)

    if title:
        repo.update_title(page_id, title)

    console.print(f"[green]更新しました: {page_id}[/green]")


@app.command()
def obsidian(
    status: str | None = typer.Option(None, "--status", help="ステータスで絞り込み (例: 未移行, 移行済み)"),
    with_body: bool = typer.Option(False, "--with-body", help="ボディ(本文)も取得する"),
) -> None:
    """Fetch and display notes from Obsidian Inbox in Notion.

    Default: show all notes.
    Use --status to filter, --with-body to include body content.
    """
    notes = sandpiper_app.list_obsidian_notes.execute(status=status, with_body=with_body)

    if not notes:
        console.print("[yellow]ノートが見つかりません[/yellow]")
        return

    console.print(f"[bold]Obsidian Inbox: {len(notes)}件[/bold]\n")
    for note in notes:
        console.print(f"[cyan bold]{note.title}[/cyan bold]")
        console.print(f"  ID: {note.page_id}")
        if note.status:
            console.print(f"  ステータス: {note.status}")
        if note.tags:
            console.print(f"  タグ: {', '.join(note.tags)}")
        if note.project_name:
            console.print(f"  プロジェクト名: {note.project_name}")
        if note.created_date:
            console.print(f"  作成日: {note.created_date}")
        if note.is_project_session:
            console.print("  プロジェクトセッション: ✓")
        if with_body and note.body:
            console.print("\n  [dim]--- ボディ ---[/dim]")
            for line in note.body.splitlines():
                console.print(f"  {line}")
        console.print()


# --- page ---


def _extract_page_id(id_or_url: str) -> str:
    """NotionのページIDまたはURLからページIDを抽出する"""
    import re
    from urllib.parse import urlparse

    # URLの場合はパスの末尾からIDを取得
    parsed = urlparse(id_or_url)
    if parsed.scheme in ("http", "https"):
        path = parsed.path.rstrip("/")
        # パスの最後のセグメントがページID (末尾の32桁16進数)
        match = re.search(r"-([0-9a-f]{32})$", path)
        if match:
            return match.group(1)
        # セグメント自体が32桁の場合
        last_segment = path.split("/")[-1]
        if re.fullmatch(r"[0-9a-f]{32}", last_segment):
            return last_segment
        msg = f"URLからページIDを抽出できませんでした: {id_or_url}"
        raise typer.BadParameter(msg)
    return id_or_url


def _block_to_markdown(block: object) -> str:
    """Lotionブロックをマークダウン文字列に変換する"""
    cls = type(block).__name__
    text = block.to_slack_text()  # type: ignore[attr-defined]
    if cls == "Heading":
        prefix = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}.get(
            block.heading_type,  # type: ignore[attr-defined]
            "#",
        )
        return f"{prefix} {text}"
    return text


@_page_app.command("get")
def page_get(
    id_or_url: str = typer.Argument(..., help="NotionページID、またはNotionページのURL"),
    raw: bool = typer.Option(False, "--raw", help="プレーンテキストをそのまま出力する"),
) -> None:
    """Notionページの本文を取得して表示します"""
    from lotion import Lotion
    from rich.markdown import Markdown

    page_id = _extract_page_id(id_or_url)
    client = Lotion.get_instance()
    page = client.retrieve_page(page_id)

    if not page.block_children:
        console.print("[yellow]本文がありません[/yellow]")
        return

    lines = [_block_to_markdown(b) for b in page.block_children]
    body = "\n".join(lines)

    if raw:
        print(body)
    else:
        console.print(Markdown(body))


if __name__ == "__main__":
    app()
