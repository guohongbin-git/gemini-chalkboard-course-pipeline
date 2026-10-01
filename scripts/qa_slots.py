#!/usr/bin/env python3
"""终态帧槽位完整性验收 —— 程序化，不靠肉眼。

METHODOLOGY §8.1：肉眼数「几个框」会漏。逐个槽位矩形测底板像素占比，
覆盖率低于阈值的槽位判为缺字。

用法：
    python3 qa_slots.py <集名> --mp4 out/smoketest.mp4 [--gap 1.6]

口径：终态帧 = 纯音频结束处（页内 audioSeconds*fps 帧），
不是「纯音频末 - 0.5s」——末项进场按 anchor 铺满，取更早会漏（METHODOLOGY §7）。
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# 板面留白框的米色区间。tag 型槽位无底板，单独排除。
CARD = (225, 252), (218, 248), (200, 235)


def card_mask(img: np.ndarray) -> np.ndarray:
    r, g, b = img[:, :, 0].astype(int), img[:, :, 1].astype(int), img[:, :, 2].astype(int)
    return (
        (r > CARD[0][0]) & (r < CARD[0][1])
        & (g > CARD[1][0]) & (g < CARD[1][1])
        & (b > CARD[2][0]) & (b < CARD[2][1])
        & ((r - b) > 8) & ((r - b) < 40)
    )


def grab(mp4: Path, frame: int, out: Path) -> np.ndarray:
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(mp4),
         "-vf", f"select='eq(n\\,{frame})'", "-vsync", "0", "-frames:v", "1", str(out)],
        check=True,
    )
    return np.array(Image.open(out).convert("RGB"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("series")
    ap.add_argument("--mp4", default=None, help="成片路径；缺省用 remotion/out/<集名>.mp4")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--render", action="store_true", help="缺失时先渲一版探针片")
    args = ap.parse_args()

    series = args.series
    tl_path = ROOT / "remotion" / "public" / series / "timeline.json"
    if not tl_path.is_file():
        print(f"错误：找不到 {tl_path}，先跑 build_timeline.py", file=sys.stderr)
        return 1
    timeline = json.loads(tl_path.read_text(encoding="utf-8"))

    mp4 = Path(args.mp4) if args.mp4 else ROOT / "remotion" / "out" / f"{series}.mp4"
    if not mp4.is_file():
        if not args.render:
            print(f"错误：找不到 {mp4}\n先渲染，或加 --render 自动渲探针片。", file=sys.stderr)
            return 1
        mp4.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["npx", "remotion", "render", f"src/series/{series}.tsx",
             f"{series}Course", str(mp4), "--codec=h264"],
            cwd=ROOT / "remotion", check=True,
        )

    fps = timeline["fps"]
    total_slots = 0
    missing: list[str] = []
    frame_cursor = 0
    probe_pages: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        for page in timeline["pages"]:
            # 终态帧：纯音频结束处，且不超过本页总长
            audio_end = frame_cursor + round(page["audioSeconds"] * fps)
            page_end = frame_cursor + round(page["pageSeconds"] * fps)
            probe = min(audio_end, page_end - 1)
            frame_cursor = page_end

            img = grab(mp4, probe, Path(td) / f"{page['id']}.png")
            mask = card_mask(img)

            # 白底探针片：底板图未就位，底板覆盖率判据不适用（METHODOLOGY §8.2）。
            # 但槽位该有没有字，仍然可以验——改成测「槽位内有非白像素」。
            is_probe = mask.mean() < 0.005
            if is_probe:
                probe_pages.append(page["id"])

            for slot in page["slots"]:
                if slot.get("noBacking") or slot.get("role") == "tag":
                    continue
                total_slots += 1
                x0, y0 = slot["x"], slot["y"]
                x1, y1 = x0 + slot["w"], y0 + slot["h"]
                x1 = min(x1, img.shape[1])
                y1 = min(y1, img.shape[0])
                patch = img[y0:y1, x0:x1]
                if is_probe:
                    # 探针片：文字是深色，底是纯白。测非白占比。
                    cov = float((patch.astype(int).sum(axis=2) < 720).mean())
                    label = "有字" if cov > 0.005 else "缺字"
                else:
                    cov = float(mask[y0:y1, x0:x1].mean())
                    label = "有底板" if cov >= args.threshold else "缺底板"
                if label.startswith("缺"):
                    missing.append(
                        f"{page['id']}/{slot['id']} {label} 覆盖 {cov:.3f} "
                        f"({slot['x']},{slot['y']} {slot['w']}x{slot['h']})"
                    )

    print(f"集 {series}: 检 {total_slots} 个槽位（tag 型不计入）")
    if probe_pages:
        print(f"  探针片页 {','.join(probe_pages)}：板面未就位，改用「槽位内有字」判据")
    if missing:
        print(f"\n异常 {len(missing)} 处：")
        for m in missing:
            print(f"  {m}")
        return 1
    print("  全部槽位通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
