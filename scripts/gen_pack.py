#!/usr/bin/env python3
"""gen_pack.py — 从紧凑 spec 生成一讲的 pack.json + narration/all.json
用法: python3 scripts/gen_pack.py <spec.json>
spec 必填字段: series, course, research, captions{s01..s08},
  s01{title,sub,hook}, s02{q,c1,c2,c3,fact},
  s03{name,why,fail}, s04{name,why,fail}, s05{name,why,fail},
  s06{rule,note}, s07{inp,out}, s08{you,next,karel}
可选: s05_pause (默认 7)
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def box(bid, text, role, size, color, align, stage, x, y, w, h):
    return {"box_id": bid, "text": text, "role": role, "font_size": size,
            "color": color, "align": align, "background": "transparent",
            "stage": stage, "rect_1920x1080_px": {"x": x, "y": y, "w": w, "h": h}}


def scene(sid, image, pause, caption, boxes):
    return {"scene_id": sid, "image": image, "pause_seconds": pause,
            "caption": caption, "boxes": boxes}


def build(s):
    ser = s["series"]
    scenes = [
        scene("s01", "boards/cs106a_s01.png", 0, s["captions"]["s01"], [
            box("title", s["s01"]["title"], "title", 58, "#F5F4E8", "left", 1, 480, 360, 980, 100),
            box("sub", s["s01"]["sub"], "subtitle", 38, "#97D9F5", "left", 1, 484, 500, 900, 64),
            box("hook", s["s01"]["hook"], "databar", 42, "#F6D87F", "left", 2, 484, 640, 760, 72),
        ]),
        scene("s02", "boards/cs106a_s02.png", 0, s["captions"]["s02"], [
            box("q", s["s02"]["q"], "body", 32, "#F6D87F", "center", 1, 460, 380, 260, 130),
            box("c1", s["s02"]["c1"], "celltext", 28, "#F5F4E8", "center", 1, 1160, 450, 170, 200),
            box("c2", s["s02"]["c2"], "celltext", 28, "#F5F4E8", "center", 1, 1385, 450, 180, 200),
            box("c3", s["s02"]["c3"], "celltext", 28, "#F5F4E8", "center", 1, 1610, 450, 180, 200),
            box("fact", s["s02"]["fact"], "databar", 34, "#97D9F5", "left", 2, 120, 920, 900, 66),
        ]),
        scene("s03", f"boards/{ser}_c1.png", 0, s["captions"]["s03"], [
            box("name", s["s03"]["name"], "celltitle", 46, "#F5F4E8", "center", 1, 190, 560, 330, 100),
            box("why", s["s03"]["why"], "body", 36, "#F6D87F", "center", 2, 690, 400, 400, 90),
            box("fail", s["s03"]["fail"], "body", 34, "#97D9F5", "center", 3, 1370, 380, 420, 140),
        ]),
        scene("s04", f"boards/{ser}_c2.png", 0, s["captions"]["s04"], [
            box("name", s["s04"]["name"], "celltitle", 46, "#F5F4E8", "center", 1, 190, 560, 330, 100),
            box("why", s["s04"]["why"], "body", 38, "#F6D87F", "center", 2, 690, 400, 400, 90),
            box("fail", s["s04"]["fail"], "body", 34, "#97D9F5", "center", 3, 1370, 380, 420, 140),
        ]),
        scene("s05", f"boards/{ser}_c3.png", s.get("s05_pause", 7), s["captions"]["s05"], [
            box("name", s["s05"]["name"], "celltitle", 54, "#F5F4E8", "center", 1, 190, 560, 330, 100),
            box("why", s["s05"]["why"], "body", 38, "#F6D87F", "center", 2, 690, 400, 400, 90),
            box("fail", s["s05"]["fail"], "body", 34, "#97D9F5", "center", 3, 1370, 380, 420, 140),
        ]),
        scene("s06", "boards/cs106a_s06.png", 0, s["captions"]["s06"], [
            box("title", "常见陷阱", "title", 60, "#F6D87F", "left", 1, 70, 70, 480, 92),
            box("rule", s["s06"]["rule"], "celltext", 38, "#F5F4E8", "center", 1, 740, 450, 480, 260),
            box("note", s["s06"]["note"], "body", 28, "#97D9F5", "center", 2, 1580, 250, 250, 150),
        ]),
        scene("s07", "boards/cs106a_s07.png", 0, s["captions"]["s07"], [
            box("title", "动手例子", "title", 60, "#F6D87F", "left", 1, 70, 70, 480, 92),
            box("inp", s["s07"]["inp"], "body", 38, "#F5F4E8", "center", 2, 170, 480, 240, 200),
            box("out", s["s07"]["out"], "body", 34, "#F5F4E8", "center", 3, 1530, 400, 260, 280),
        ]),
        scene("s08", "boards/cs106a_s08.png", 0, s["captions"]["s08"], [
            box("you", s["s08"]["you"], "celltitle", 60, "#F5F4E8", "center", 1, 460, 690, 230, 200),
            box("next", s["s08"]["next"], "databar", 44, "#F6D87F", "center", 2, 1240, 500, 340, 120),
            box("karel", s["s08"]["karel"], "celltitle", 44, "#F5F4E8", "center", 2, 1670, 470, 200, 180),
        ]),
    ]
    pack = {
        "schema_version": "1.0",
        "course": s["course"],
        "board_basis": "1672x941 源图，槽位坐标为 rect_1920x1080_px",
        "research_notes": s["research"],
        "scenes": scenes,
    }
    vdir = ROOT / f"{ser}_video"
    (vdir / "narration").mkdir(parents=True, exist_ok=True)
    (vdir / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    (vdir / "narration" / "all.json").write_text(
        json.dumps({k: s["captions"][k] for k in sorted(s["captions"])}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    total = sum(len(v) for v in s["captions"].values())
    print(f"{ser}: pack + narration ready, {total} 字")


if __name__ == "__main__":
    build(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")))
