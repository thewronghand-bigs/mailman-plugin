#!/bin/bash
# mailman-plugin: 원클릭 설치
# 사용: git clone → cd mailman-plugin → bash bootstrap.sh
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_PLUGIN_DIR="$HOME/plugins/mailman"
MARKETPLACE_DIR="$HOME/.agents/plugins"
MARKETPLACE_FILE="$MARKETPLACE_DIR/marketplace.json"

echo "[mailman] 설치를 시작합니다."

# 1. 플러그인 위치 확인/복사
mkdir -p "$HOME/plugins" "$MARKETPLACE_DIR"

if [ "$PLUGIN_ROOT" != "$HOME_PLUGIN_DIR" ]; then
  echo "[mailman] 플러그인을 $HOME_PLUGIN_DIR 로 복사합니다."
  rm -rf "$HOME_PLUGIN_DIR"
  cp -r "$PLUGIN_ROOT" "$HOME_PLUGIN_DIR"
  PLUGIN_ROOT="$HOME_PLUGIN_DIR"
  echo "[mailman] 복사 완료."
fi

# 2. bun 확인
if ! command -v bun >/dev/null 2>&1; then
  echo "[mailman] bun이 설치되어 있지 않습니다."
  echo "  curl -fsSL https://bun.sh/install | bash"
  echo "  설치 후 이 스크립트를 다시 실행하세요."
  exit 1
fi

# 3. 의존성 설치
cd "$PLUGIN_ROOT/runtime"
bun install

# 4. Playwright 브라우저 설치
echo "[mailman] Playwright Chromium을 설치합니다..."
bunx playwright install chromium

# 5. config.json 생성
if [ ! -f config.json ]; then
  cp config.example.json config.json
  echo "[mailman] runtime/config.json 생성됨. 반드시 본인 환경에 맞게 수정하세요."
fi

# 6. marketplace.json 등록
if [ ! -f "$MARKETPLACE_FILE" ]; then
  cat > "$MARKETPLACE_FILE" <<'EOF'
{
  "name": "company-local",
  "interface": {
    "displayName": "Company Local"
  },
  "plugins": []
}
EOF
fi

python3 - "$MARKETPLACE_FILE" <<'PY'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
plugins = data.setdefault("plugins", [])

entry = {
    "name": "mailman",
    "source": {"source": "local", "path": "./plugins/mailman"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Productivity"
}

plugins = [p for p in plugins if p.get("name") != "mailman"]
plugins.append(entry)
data["plugins"] = plugins
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
PY

echo ""
echo "============================================"
echo "[mailman] 설치 완료!"
echo "============================================"
echo ""
echo "다음 단계:"
echo ""
echo "  1. config.json 수정:"
echo "     vi $PLUGIN_ROOT/runtime/config.json"
echo ""
echo "  2. 최초 Google 로그인:"
echo "     bash $PLUGIN_ROOT/runtime/run.sh auth"
echo ""
echo "  3. Codex Desktop을 재시작하면 @mailman 사용 가능"
echo ""
