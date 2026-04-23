#!/bin/bash
# mailman-plugin: on-demand 수집 래퍼
# 사용법:
#   run.sh           → collector 1회 실행 (기본)
#   run.sh auth      → 최초 로그인 세션 셋업

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAILMAN_HOME="${MAILMAN_HOME:-$HOME/.mailman}"
LOG_FILE="$MAILMAN_HOME/logs/mailman.log"
mkdir -p "$(dirname "$LOG_FILE")"

if [ -z "$PATH_ADDED" ]; then
  export PATH="$HOME/.bun/bin:$HOME/.nvm/versions/node/v24.11.1/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
  export PATH_ADDED=1
fi

BUN_BIN="$(command -v bun || echo "$HOME/.nvm/versions/node/v24.11.1/bin/bun")"

if [ ! -x "$BUN_BIN" ]; then
  echo "[mailman] $(date -Iseconds) bun not found at $BUN_BIN" >> "$LOG_FILE"
  exit 1
fi

cd "$SCRIPT_DIR"

if [ "${1:-}" = "auth" ]; then
  shift
  "$BUN_BIN" run auth.ts "$@"
  exit $?
fi

# 수집 모드: 모든 인자를 collector.ts에 전달 (스페이스 별칭 등)
"$BUN_BIN" run collector.ts "$@" 2>> "$LOG_FILE"
rc=$?

if [ $rc -eq 2 ] || [ $rc -eq 3 ]; then
  echo "[mailman] 로그인 세션이 없거나 만료되었습니다. 다음 명령을 실행하세요:"
  echo "  bash $(pwd)/run.sh auth"
fi

exit 0
