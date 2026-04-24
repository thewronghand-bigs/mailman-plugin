#!/bin/bash
# mailman-plugin: 원라인 설치
# 사용: curl -fsSL https://raw.githubusercontent.com/thewronghand-bigs/mailman-plugin/main/install.sh | bash
set -euo pipefail

REPO="thewronghand-bigs/mailman-plugin"
BRANCH="main"
PLUGIN_DIR="$HOME/plugins/mailman"

echo "[mailman] 설치를 시작합니다."

# 1. bun 확인
if ! command -v bun >/dev/null 2>&1; then
  echo "[mailman] bun이 설치되어 있지 않습니다."
  echo "  curl -fsSL https://bun.sh/install | bash"
  echo "  설치 후 다시 실행하세요."
  exit 1
fi

# 2. 플러그인 다운로드
mkdir -p "$PLUGIN_DIR"

if command -v git >/dev/null 2>&1; then
  if [ -d "$PLUGIN_DIR/.git" ]; then
    echo "[mailman] 기존 설치 업데이트 중..."
    cd "$PLUGIN_DIR" && git pull --ff-only
  else
    rm -rf "$PLUGIN_DIR"
    git clone --depth 1 "https://github.com/$REPO.git" "$PLUGIN_DIR"
  fi
else
  echo "[mailman] git 없이 tarball로 설치합니다..."
  TMP_TAR="$(mktemp)"
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz" -o "$TMP_TAR"
  rm -rf "$PLUGIN_DIR"
  mkdir -p "$PLUGIN_DIR"
  tar xzf "$TMP_TAR" --strip-components=1 -C "$PLUGIN_DIR"
  rm -f "$TMP_TAR"
fi

# 3. 의존성 설치
cd "$PLUGIN_DIR/runtime"
bun install

# 4. Playwright Chromium 설치
echo "[mailman] Playwright Chromium 설치 중..."
bunx playwright install chromium

# 5. config.json 생성
if [ ! -f config.json ]; then
  cp config.example.json config.json
  echo "[mailman] runtime/config.json 생성됨."
fi

# 6. marketplace.json 등록
MARKETPLACE_DIR="$HOME/.agents/plugins"
MARKETPLACE_FILE="$MARKETPLACE_DIR/marketplace.json"
mkdir -p "$MARKETPLACE_DIR"

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
echo "     vi $PLUGIN_DIR/runtime/config.json"
echo ""
echo "  2. 최초 Google 로그인:"
echo "     bash $PLUGIN_DIR/runtime/run.sh auth"
echo ""
echo "  3. Codex Desktop 재시작 → @mailman 사용 가능"
echo ""
