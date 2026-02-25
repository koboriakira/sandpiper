#!/bin/bash
# cron-runner.sh - Sandpiper CLIコマンドをcronから安全に実行するためのラッパースクリプト
#
# 使い方:
#   scripts/cron-runner.sh <sandpiper-command> [options...]
#
# 例:
#   scripts/cron-runner.sh sync-jira-to-project --notify
#   scripts/cron-runner.sh archive-old-todos --notify
#
# crontab設定例:
#   # JIRA同期 (平日2時間おき)
#   0 */2 * * 1-5 /path/to/sandpiper/scripts/cron-runner.sh sync-jira-to-project --notify
#   # TODOアーカイブ (毎週日曜3:00)
#   0 3 * * 0 /path/to/sandpiper/scripts/cron-runner.sh archive-old-todos --notify

set -euo pipefail

# プロジェクトルートを基準にパスを解決
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ログ設定
LOG_DIR="/tmp"
LOG_FILE="${LOG_DIR}/sandpiper-cron.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# 引数チェック
if [ $# -eq 0 ]; then
    echo "Usage: $0 <sandpiper-command> [options...]" >&2
    exit 1
fi

COMMAND="$*"

log "START: sandpiper $COMMAND"

# .envファイルの読み込み (dotenvの代替としてシェルで直接読み込み)
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "$PROJECT_DIR/.env"
    set +a
fi

# uvコマンドの実行
cd "$PROJECT_DIR"
if uv run sandpiper $COMMAND >> "$LOG_FILE" 2>&1; then
    log "END: sandpiper $COMMAND (success)"
else
    EXIT_CODE=$?
    log "END: sandpiper $COMMAND (failed with exit code $EXIT_CODE)"
    exit $EXIT_CODE
fi
