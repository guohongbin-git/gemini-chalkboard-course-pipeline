#!/usr/bin/env bash
# 重建 TTS venv。必须用 Homebrew python3.10：uv 版缺编译头，wheel 也坏。
set -euo pipefail
ROOT="$(cd -P "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/tts/venv"
PY310="/opt/homebrew/bin/python3.10"

rm -rf "$VENV"
"$PY310" -m venv "$VENV"
P="$VENV/bin/python"

export PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.org/simple/}"
export SDKROOT="${SDKROOT:-$(xcrun --sdk macosx --show-sdk-path)}"
export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-11.0}"

"$P" -m pip install -q --upgrade pip

echo "==> numpy 2.2.6"
"$P" -m pip install -q "numpy==2.2.6"

# scipy>=1.15 的 _propack 在本机 macOS 上 dyld 拒绝加载（__thread_bss 段），
# 而 mlx_audio.resample 只要 `from scipy import signal`，会被连带拖垮。锁 1.14.1。
echo "==> scipy 1.14.1 (1.15.x 的 propack 扩展在本机无法加载)"
"$P" -m pip install -q "scipy==1.14.1"

echo "==> mlx-audio 0.5.6 / mlx 0.32.2"
"$P" -m pip install -q "mlx-audio==0.5.6" "mlx==0.32.2"

echo "==> 校验"
"$P" - <<'PY'
import importlib.metadata as md
import numpy, scipy
from scipy import signal
import mlx.core as mx
import mlx_audio
for p in ("mlx", "mlx-audio", "numpy", "scipy", "transformers"):
    print(f"  {p:12s} {md.version(p)}")
print("  scipy.signal  OK")
print("  mlx device    ", mx.default_device())
print("  mlx compute   ", (mx.array([1.0, 2.0]) * 3).tolist())
PY

echo
echo "完成。缺 torch 不影响 TTS 主链路（mlx_audio 走 MLX，不经 torch）。"
