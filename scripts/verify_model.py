#!/usr/bin/env python3
"""校验 TTS 模型完整性：tensor 可读、配置齐备。不加载进内存，秒级完成。"""
import json
import sys
from pathlib import Path

from safetensors import safe_open
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "tts" / "models" / "qwen3" / "Base-1.7B"

REQUIRED = [
    "config.json",
    "generation_config.json",
    "model.safetensors",
    "preprocessor_config.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "speech_tokenizer/config.json",
    "speech_tokenizer/model.safetensors",
]

fail = 0

missing = [f for f in REQUIRED if not (MODEL / f).exists()]
for f in missing:
    print(f"  MISSING  {f}")
    fail += 1
if missing:
    print(f"\n失败：缺 {len(missing)} 个文件")
    sys.exit(1)

cfg = json.loads((MODEL / "config.json").read_text())
print(f"  arch      {cfg.get('architectures')}")
print(f"  model_type {cfg.get('model_type')}")

for rel in ("model.safetensors", "speech_tokenizer/model.safetensors"):
    path = MODEL / rel
    with safe_open(str(path), framework="np") as f:
        keys = list(f.keys())
        # 只读元数据：bfloat16 无法物化为 numpy 数组，但切片/shape 可查。
        declared = sum(
            int(__import__("math").prod(f.get_slice(k).get_shape()))
            for k in keys
        )
        size_mb = path.stat().st_size / 1e6
        print(
            f"  {rel:38s} {len(keys):5d} tensors  {size_mb:8.1f} MB  "
            f"({declared:,} elems)"
        )

print("\n模型完整性通过" if not fail else "\n失败")
sys.exit(fail)
