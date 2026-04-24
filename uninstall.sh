#!/bin/bash
# mailman-plugin: 삭제
# 사용: curl -fsSL https://raw.githubusercontent.com/thewronghand-bigs/mailman-plugin/main/uninstall.sh | bash
set -euo pipefail

PLUGIN_DIR="$HOME/plugins/mailman"
DATA_DIR="$HOME/.mailman"
MARKETPLACE_FILE="$HOME/.agents/plugins/marketplace.json"

echo "[mailman] 삭제를 시작합니다."

# 1. 플러그인 삭제
if [ -d "$PLUGIN_DIR" ]; then
  rm -rf "$PLUGIN_DIR"
  echo "[mailman] 플러그인 삭제: $PLUGIN_DIR"
else
  echo "[mailman] 플러그인이 없습니다: $PLUGIN_DIR"
fi

# 2. marketplace.json에서 mailman 항목 제거
if [ -f "$MARKETPLACE_FILE" ]; then
  python3 - "$MARKETPLACE_FILE" <<'PY'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
plugins = data.get("plugins", [])
data["plugins"] = [p for p in plugins if p.get("name") != "mailman"]
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
PY
  echo "[mailman] marketplace.json에서 제거 완료"
fi

# 3. 데이터 삭제 확인
if [ -d "$DATA_DIR" ]; then
  echo ""
  echo "[mailman] 수집된 데이터가 남아 있습니다: $DATA_DIR"
  echo "  (DB, Chrome 프로필, 로그)"
  echo "  완전히 삭제하려면: rm -rf $DATA_DIR"
else
  echo "[mailman] 데이터 없음."
fi

echo ""
echo "[mailman] 삭제 완료. Codex Desktop을 재시작하세요."
