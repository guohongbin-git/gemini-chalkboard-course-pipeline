#!/usr/bin/env python3
"""install_boards.py — 把 /tmp 出的 3 张概念板图缩放到 1672x941 装入 boards/ 并更新 pack.json
用法: python3 scripts/install_boards.py <series> <c1_png> <c2_png> <c3_png>
"""
import json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ser, c1, c2, c3 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    boards = ROOT / "remotion" / "public" / "boards"
    for i, src in enumerate([c1, c2, c3], 1):
        dst = boards / f"{ser}_c{i}.png"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", src,
            "-vf", "scale=1672:941:force_original_aspect_ratio=increase,crop=1672:941",
            str(dst)], check=True)
    ppath = ROOT / f"{ser}_video" / "pack.json"
    d = json.loads(ppath.read_text(encoding="utf-8"))
    for idx in (2, 3, 4):
        d["scenes"][idx]["image"] = f"boards/{ser}_c{idx - 1}.png"
    ppath.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{ser}: boards installed, pack updated")


if __name__ == "__main__":
    main()
