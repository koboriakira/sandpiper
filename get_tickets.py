#!/usr/bin/env python3
"""
SUプロジェクトのチケットを柔軟な条件で検索する汎用スクリプト

使用方法:
    python get_tickets.py [オプション]

オプション:
    -s, --status <status>           ステータス (例: "To Do", "In Progress", "Done")
    -t, --type <types>              Issue Type カンマ区切り (例: "Epic", "Story,Task,Bug")
    -v, --fix-version <version>     Fix Version (例: "FY25_3Q", "10470")
                                    数値のみの場合はID、それ以外は名前として扱う
    -p, --sprint <sprint>           Sprint名 (例: "Sprint 25")
    -a, --assignee <assignee>       Assignee (例: "cmdkhandoker", "a_kobori@codmon.co.jp")
    -l, --labels <labels>           Labels カンマ区切り (例: "問い合わせ対応,バグ修正")
    -d, --start-date <date>         Start date (例: "2025-01-01", ">= 2025-01-01", "< 2025-02-01")
    -e, --actual-end <date>         Actual end (例: "2025-01-01", ">= 2025-01-01", "< 2025-02-01")
    -u, --updated <date>            Last update (例: "2025-01-01", ">= -7d")
    -f, --fields <fields>           出力フィールド カンマ区切り (例: "key,summary,status")
                                    利用可能: key,summary,status,type,assignee,priority,fixVersions,sprint,startDate,
                                             created,updated,githubIssue,slackUrl,doneComment,storyPoints,dueDate,labels,parent,actualEnd
                                    デフォルト: 全フィールド
    -m, --max-results <num>         最大取得件数 (デフォルト: 100)
    -o, --output <file>             出力ファイル (省略時は標準出力)
    -h, --help                      ヘルプを表示

例:
    python get_tickets.py -s "To Do" -t "Epic" -m 50
    python get_tickets.py -s "In Progress" -v "2025-01-15"
    python get_tickets.py -u ">= -7d" -t "Bug,Task"
    python get_tickets.py -p "Sprint 25" -s "Done"
"""

import argparse
import json
import os
import re
import sys
from typing import Any

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# フィールド名マッピング
FIELD_MAPPING = {
    'key': 'key',
    'summary': 'summary',
    'status': 'status',
    'type': 'issuetype',
    'assignee': 'assignee',
    'priority': 'priority',
    'fixVersions': 'fixVersions',
    'sprint': 'customfield_10020',
    'startDate': 'customfield_10015',
    'created': 'created',
    'updated': 'updated',
    'githubIssue': 'customfield_10328',
    'slackUrl': 'customfield_10262',
    'doneComment': 'customfield_10096',
    'storyPoints': 'customfield_10026',
    'dueDate': 'duedate',
    'labels': 'labels',
    'parent': 'parent',
    'actualEnd': 'customfield_10009',
}

# デフォルトフィールド
DEFAULT_FIELDS = [
    'key', 'summary', 'status', 'type', 'assignee', 'priority',
    'fixVersions', 'sprint', 'startDate', 'created', 'updated',
    'githubIssue', 'slackUrl', 'doneComment', 'storyPoints',
    'dueDate', 'labels', 'parent', 'actualEnd'
]


class JiraClient:
    """Jira API クライアント"""

    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url
        self.username = username
        self.api_token = api_token
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({'Accept': 'application/json'})

    def search_issues(
        self,
        jql: str,
        fields: list[str],
        max_results: int = 100
    ) -> list[dict[str, Any]]:
        """
        JQLクエリでチケットを検索（ページネーション対応）

        Args:
            jql: JQLクエリ文字列
            fields: 取得するフィールドのリスト
            max_results: 最大取得件数

        Returns:
            チケットのリスト
        """
        url = f"{self.base_url}/rest/api/3/search/jql"
        all_issues = []
        next_page_token = None
        fetched_count = 0

        while fetched_count < max_results:
            # 残り取得数を計算（最大100件ずつ）
            remaining = max_results - fetched_count
            page_size = min(remaining, 100)

            # パラメータを構築
            params = {
                'jql': jql,
                'fields': ','.join(fields),
                'maxResults': page_size
            }

            if next_page_token:
                params['nextPageToken'] = next_page_token

            # API呼び出し
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error: Failed to call Jira API: {e}", file=sys.stderr)
                sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON response: {e}", file=sys.stderr)
                sys.exit(1)

            # エラーチェック
            if 'errorMessages' in data:
                print("Error from Jira API:", file=sys.stderr)
                print(json.dumps(data['errorMessages'], indent=2), file=sys.stderr)
                sys.exit(1)

            # issuesを追加
            issues = data.get('issues', [])
            all_issues.extend(issues)
            fetched_count += len(issues)

            # ページネーション情報
            next_page_token = data.get('nextPageToken')
            is_last = data.get('isLast', False)

            # 終了条件
            if is_last or len(issues) == 0 or not next_page_token:
                break

        return all_issues


def build_jql_query(
    status: str | None = None,
    issue_types: str | None = None,
    fix_version: str | None = None,
    sprint: str | None = None,
    assignee: str | None = None,
    labels: str | None = None,
    start_date: str | None = None,
    actual_end: str | None = None,
    updated: str | None = None
) -> str:
    """
    JQLクエリを動的に構築

    Args:
        status: ステータス
        issue_types: Issue Type（カンマ区切り）
        fix_version: Fix Version
        sprint: Sprint名
        assignee: Assignee
        labels: Labels（カンマ区切り）
        start_date: Start date条件
        actual_end: Actual end条件
        updated: Updated条件

    Returns:
        JQLクエリ文字列
    """
    conditions = ["project = SU"]

    # Status条件
    if status:
        conditions.append(f'status = "{status}"')

    # Issue Type条件
    if issue_types:
        types_list = [t.strip() for t in issue_types.split(',')]
        if len(types_list) == 1:
            conditions.append(f'type = {types_list[0]}')
        else:
            types_str = ', '.join(f'"{t}"' for t in types_list)
            conditions.append(f'type IN ({types_str})')

    # Fix Version条件
    if fix_version:
        # 数値のみの場合はID、それ以外は名前として扱う
        if fix_version.isdigit():
            conditions.append(f'fixVersion = {fix_version}')
        else:
            conditions.append(f'fixVersion = "{fix_version}"')

    # Sprint条件
    if sprint:
        conditions.append(f'sprint = "{sprint}"')

    # Assignee条件
    if assignee:
        conditions.append(f'assignee = "{assignee}"')

    # Labels条件
    if labels:
        labels_list = [l.strip() for l in labels.split(',')]
        if len(labels_list) == 1:
            conditions.append(f'labels = "{labels_list[0]}"')
        else:
            labels_str = ', '.join(f'"{l}"' for l in labels_list)
            conditions.append(f'labels IN ({labels_str})')

    # Start date条件
    if start_date:
        # ">= 2025-01-01" のような形式をサポート
        match = re.match(r'^([<>=]+)\s*(.+)$', start_date)
        if match:
            operator, date_value = match.groups()
            conditions.append(f'"Start date" {operator} "{date_value}"')
        else:
            conditions.append(f'"Start date" = "{start_date}"')

    # Actual end条件
    if actual_end:
        # ">= 2025-01-01" のような形式をサポート
        match = re.match(r'^([<>=]+)\s*(.+)$', actual_end)
        if match:
            operator, date_value = match.groups()
            conditions.append(f'"Actual end" {operator} "{date_value}"')
        else:
            conditions.append(f'"Actual end" = "{actual_end}"')

    # Updated条件
    if updated:
        # ">= -7d" のような形式をサポート
        match = re.match(r'^([<>=]+)\s*(.+)$', updated)
        if match:
            operator, date_value = match.groups()
            conditions.append(f'updated {operator} {date_value}')
        else:
            conditions.append(f'updated >= "{updated}"')

    jql = ' AND '.join(conditions)
    jql += ' ORDER BY created DESC'

    return jql


def extract_field_value(issue: dict[str, Any], field: str, base_url: str) -> Any:
    """
    チケットから指定フィールドの値を抽出

    Args:
        issue: チケットデータ
        field: フィールド名
        base_url: Jira Base URL

    Returns:
        フィールドの値
    """
    fields = issue.get('fields', {})

    if field == 'key':
        return issue.get('key')
    elif field == 'summary':
        return fields.get('summary')
    elif field == 'status':
        return fields.get('status', {}).get('name')
    elif field == 'type':
        return fields.get('issuetype', {}).get('name')
    elif field == 'assignee':
        assignee = fields.get('assignee')
        return assignee.get('displayName') if assignee else 'Unassigned'
    elif field == 'priority':
        priority = fields.get('priority')
        return priority.get('name') if priority else 'None'
    elif field == 'fixVersions':
        versions = fields.get('fixVersions', [])
        return [v.get('name') for v in versions] if versions else []
    elif field == 'sprint':
        sprints = fields.get('customfield_10020', [])
        if sprints:
            return [s.get('name') for s in sprints
                    if s.get('state') in ['active', 'future']]
        return []
    elif field == 'startDate':
        return fields.get('customfield_10015')
    elif field == 'created':
        created = fields.get('created', '')
        return created.split('T')[0] if created else None
    elif field == 'updated':
        updated = fields.get('updated', '')
        return updated.split('T')[0] if updated else None
    elif field == 'githubIssue':
        return fields.get('customfield_10328')
    elif field == 'slackUrl':
        return fields.get('customfield_10262')
    elif field == 'doneComment':
        return fields.get('customfield_10096')
    elif field == 'storyPoints':
        return fields.get('customfield_10026')
    elif field == 'dueDate':
        return fields.get('duedate')
    elif field == 'labels':
        return fields.get('labels', [])
    elif field == 'parent':
        parent = fields.get('parent')
        return parent.get('key') if parent else None
    elif field == 'actualEnd':
        return fields.get('customfield_10009')

    return None


def format_output(
    issues: list[dict[str, Any]],
    requested_fields: list[str],
    max_results: int,
    base_url: str
) -> dict[str, Any]:
    """
    出力形式に整形

    Args:
        issues: チケットのリスト
        requested_fields: 出力するフィールドのリスト
        max_results: 最大結果数
        base_url: Jira Base URL

    Returns:
        整形された結果
    """
    formatted_issues = []

    for issue in issues:
        formatted_issue = {}

        for field in requested_fields:
            formatted_issue[field] = extract_field_value(issue, field, base_url)

        # URLは常に含める
        key = issue.get('key')
        formatted_issue['url'] = f"{base_url}/browse/{key}"

        formatted_issues.append(formatted_issue)

    return {
        'count': len(formatted_issues),
        'maxResults': max_results,
        'issues': formatted_issues
    }


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='SUプロジェクトのチケットを柔軟な条件で検索する汎用スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
    python get_tickets.py -s "To Do" -t "Epic" -m 50
    python get_tickets.py -s "In Progress" -v "2025-01-15"
    python get_tickets.py -u ">= -7d" -t "Bug,Task"
    python get_tickets.py -p "Sprint 25" -s "Done"
        """
    )

    parser.add_argument('-s', '--status', help='ステータス (例: "To Do", "In Progress", "Done")')
    parser.add_argument('-t', '--type', dest='issue_types',
                        help='Issue Type カンマ区切り (例: "Epic", "Story,Task,Bug")')
    parser.add_argument('-v', '--fix-version',
                        help='Fix Version (例: "FY25_3Q", "10470")')
    parser.add_argument('-p', '--sprint', help='Sprint名 (例: "Sprint 25")')
    parser.add_argument('-a', '--assignee',
                        help='Assignee (例: "cmdkhandoker", "a_kobori@codmon.co.jp")')
    parser.add_argument('-l', '--labels',
                        help='Labels カンマ区切り (例: "問い合わせ対応,バグ修正")')
    parser.add_argument('-d', '--start-date',
                        help='Start date (例: "2025-01-01", ">= 2025-01-01")')
    parser.add_argument('-e', '--actual-end',
                        help='Actual end (例: "2025-01-01", ">= 2025-01-01")')
    parser.add_argument('-u', '--updated',
                        help='Last update (例: "2025-01-01", ">= -7d")')
    parser.add_argument('-f', '--fields',
                        help='出力フィールド カンマ区切り (デフォルト: 全フィールド)')
    parser.add_argument('-m', '--max-results', type=int, default=100,
                        help='最大取得件数 (デフォルト: 100)')
    parser.add_argument('-o', '--output', help='出力ファイル (省略時は標準出力)')

    args = parser.parse_args()

    # 環境変数チェック
    username = os.environ.get('COPILOT_MCP_JIRA_USERNAME')
    api_token = os.environ.get('COPILOT_MCP_JIRA_API_TOKEN')

    if not username:
        print("Error: COPILOT_MCP_JIRA_USERNAME is not set", file=sys.stderr)
        sys.exit(1)

    if not api_token:
        print("Error: COPILOT_MCP_JIRA_API_TOKEN is not set", file=sys.stderr)
        sys.exit(1)

    # 出力フィールドの処理
    if args.fields:
        requested_fields = [f.strip() for f in args.fields.split(',')]
        # 不明なフィールドを警告
        for field in requested_fields:
            if field not in FIELD_MAPPING:
                print(f"Warning: Unknown field '{field}' ignored", file=sys.stderr)
        requested_fields = [f for f in requested_fields if f in FIELD_MAPPING]
    else:
        requested_fields = DEFAULT_FIELDS

    # API用フィールドリスト
    api_fields = [FIELD_MAPPING[f] for f in requested_fields if f in FIELD_MAPPING]

    # JQLクエリを構築
    jql = build_jql_query(
        status=args.status,
        issue_types=args.issue_types,
        fix_version=args.fix_version,
        sprint=args.sprint,
        assignee=args.assignee,
        labels=args.labels,
        start_date=args.start_date,
        actual_end=args.actual_end,
        updated=args.updated
    )

    # Jiraクライアント作成
    base_url = "https://codmon.atlassian.net"
    client = JiraClient(base_url, username, api_token)

    # チケットを検索
    issues = client.search_issues(jql, api_fields, args.max_results)

    # 出力を整形
    result = format_output(issues, requested_fields, args.max_results, base_url)

    # JSON出力
    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == '__main__':
    main()
