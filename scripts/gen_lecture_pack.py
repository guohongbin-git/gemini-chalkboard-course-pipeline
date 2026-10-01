#!/usr/bin/env python3
"""从 stanford-cs-learning-packs 的 IR 生成讲次级视频资源包。

输入：course_ir.json + concepts.json（仓库）+ 本文件的 LECTURES 映射表
输出：cs106a_lNN_video/pack.json + narration/all.json + board_prompts.json

8 场模板（L01 试点的结构泛化）：
  s01 片头  s02 本讲问题  s03-s05 核心概念（定义/为什么/失败条件）
  s06 陷阱  s07 例子  s08 总结与下讲预告
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/guohongbin/1-Projects/stanford-cs-learning-packs")
ROOT = Path(__file__).resolve().parent.parent

# 讲次 → (周, 概念列表, 视觉主体[黑板画面中心画什么], 下讲预告)
LECTURES = {
    2: dict(week="w1", title="Karel Commands, Methods, and Loops",
            concepts=["Karel the Robot", "Control Flow", "Method Decomposition"],
            visual="一个粉笔迷宫网格，网格里一个方头方身圆眼睛的极简小机器人，网格外一个空白小气泡",
            next_lecture="分解与前后置条件"),
    3: dict(week="w1", title="Decomposition and Pre/Post-Conditions",
            concepts=["Method Decomposition", "Control Flow", "Karel the Robot"],
            visual="一层层嵌套的粉笔方框（大框套小框），像被逐级拆解的任务清单，旁边一个空白气泡",
            next_lecture="布尔表达式与作用域"),
    6: dict(week="w1", title="Boolean Expressions, Scope, Control Statements",
            concepts=["Boolean Logic", "Variable Scope", "Control Flow"],
            visual="一个粉笔分支路口（一条路分成两条），路口上悬浮一个空白菱形框，旁边一个空白小卡片",
            next_lecture="字符串处理与分词"),
    13: dict(week="w2", title="String Processing and Tokenizers",
             concepts=["String Manipulation", "Control Flow"],
             visual="一串粉笔小方块排成一行（像字符序列），一把小剪刀把序列切成几段，旁边一个空白气泡",
             next_lecture="文件、异常与输入输出"),
    15: dict(week="w2", title="Files, Exceptions, and I/O",
             concepts=["File I/O", "String Manipulation"],
             visual="一个粉笔文件夹图标，几条数据线从文件夹流入一台小屏幕，旁边一个警示三角形和空白气泡",
             next_lecture="数组与数组操作"),
    16: dict(week="w2", title="Arrays and Array Operations",
             concepts=["Array", "Control Flow"],
             visual="一排编号的粉笔储物格（4-6 格），每格上方一个小圆圈序号位，旁边一个空白气泡",
             next_lecture="多维数组与 ArrayList"),
    17: dict(week="w2", title="Multidimensional Arrays and ArrayList",
             concepts=["Array", "ArrayList"],
             visual="粉笔画的棋盘网格（行列结构），网格旁边一列可伸缩的弹性方框，一个空白气泡",
             next_lecture="写自己的类"),
    9: dict(week="w3", title="Writing Your Own Class, Constructor, Visibility",
            concepts=["Class", "Object-Oriented Design"],
            visual="一个粉笔图纸（蓝图卷轴打开），图纸上一个齿轮轮廓，旁边三个大小递进的空白方框",
            next_lecture="继承、重写与接口"),
    10: dict(week="w3", title="Extending a Class, Overriding Methods, Interfaces",
             concepts=["Inheritance", "Interface", "Class"],
             visual="粉笔家谱树（一根主干分出两根枝），枝头两个小方框，旁边一个空白气泡",
             next_lecture="调试方法与 Eclipse 调试器"),
    18: dict(week="w3", title="Debugging Approaches and the Eclipse Debugger",
             concepts=["Debugging", "Control Flow"],
             visual="一个粉笔放大镜盖在几行波浪线上，放大镜柄外一个空白的便签框，旁边一个空白气泡",
             next_lecture="接口与重写方法"),
    11: dict(week="w4", title="Interfaces and Overriding Methods",
             concepts=["Interface", "Inheritance", "Polymorphism"],
             visual="两个形状相同但大小不同的粉笔插头与插座，中间一条虚线连接，旁边一个空白气泡",
             next_lecture="事件驱动程序"),
    11.1: dict(week="w4", title="Event-Driven Programs: Mouse and Keyboard Events",
               concepts=["Event Handler", "Graphics Program"],
               visual="一个粉笔鼠标和一个键盘，各自发出一条弧线箭头汇聚到中央一个空白方框",
               next_lecture="异常与按引用传递"),
    15.1: dict(week="w4", title="Exceptions and Call-by-Reference Objects",
               concepts=["Exception Handling", "Polymorphism"],
               visual="一个粉笔警示三角（内含感叹号位置留白），三角旁一条被拦断的箭头线，一个空白气泡",
               next_lecture="查找、排序与算法效率"),
    23: dict(week="w5", title="Searching, Sorting and Algorithmic Efficiency",
             concepts=["Algorithm Analysis", "Big O Notation", "Searching and Sorting"],
             visual="粉笔坐标轴（横轴纵轴留白），轴上一条陡峭曲线和一条平缓曲线，旁边两个空白小卡片",
             next_lecture="信息隐藏与参数传递"),
    8: dict(week="w6", title="Information Hiding, Parameter Passing, Instance vs Local Variables",
            concepts=["Encapsulation", "Parameter Passing", "Static Method"],
            visual="一个粉笔盒子（盒盖半开），盒内一个齿轮被虚线圈住，盒外两个小方框与盒子之间两条箭头",
            next_lecture="构造器与 this 关键字"),
    8.1: dict(week="w6", title="Constructors and the this Keyword",
              concepts=["Constructor", "Class", "Encapsulation"],
              visual="一个粉笔工厂大门，门内传送带送出两个相同的小方块，一个空白气泡",
              next_lecture="Map 集合与迭代器"),
    19: dict(week="w6", title="A Map, HashMap, Collection Hierarchy and Iterator",
             concepts=["HashMap and Map Collections", "Iterator", "Data Abstraction"],
             visual="粉笔钥匙串（一把大钥匙带三把小钥匙），每把钥匙对着一个空白小方框，一个空白气泡",
             next_lecture="变量、类型与图形坐标"),
    5: dict(week="w7", title="Variables, Data Types and Graphics Coordinates",
            concepts=["Primitive Type", "Reference Type", "Coordinate System"],
            visual="粉笔坐标网格（横纵轴带刻度留白），网格中一个空心圆点，两个空白标签框",
            next_lecture="类型转换、常量与运算符"),
    6.1: dict(week="w7", title="Type Casting, Constants and Operators",
              concepts=["Casting", "Primitive Type", "Reference Type"],
              visual="两个粉笔容器（一大一小），小容器往大容器倒液体，中间一个加号，旁边一个空白气泡",
              next_lecture="线性二分查找与排序"),
    7: dict(week="w7", title="Linear and Binary Search, Selection and Radix Sort",
            concepts=["Searching and Sorting", "Algorithm Analysis"],
            visual="一排粉笔竖条（高矮不一，像排序柱状图），一条折线箭头依次扫过它们，一个空白气泡",
            next_lecture="图形坐标与 GObject 层次"),
    5.1: dict(week="w8", title="Graphics Coordinates and the GObject Hierarchy",
             concepts=["Graphics Object", "Coordinate System", "Data Abstraction"],
             visual="粉笔画的画框（里面一个圆一个方一个三角），框外一个家谱式的小树，一个空白气泡",
             next_lecture="响应鼠标与键盘事件"),
    11.2: dict(week="w8", title="Responding to Mouse and Keyboard Events",
               concepts=["Mouse Listener", "Keyboard Listener", "Event Handler"],
               visual="粉笔鼠标与键盘（上下排列），各拖一条弧线指向中央空白画布框",
               next_lecture="Swing 组件与交互器"),
    20: dict(week="w8", title="Swing Interactor Hierarchy and Creating Interactors",
             concepts=["Swing Components", "Data Abstraction", "Event Handler"],
             visual="粉笔界面草图：一个窗口框内有按钮、滑杆、下拉框的极简线稿，旁边一个空白气泡",
             next_lecture="JavaDoc 与文档"),
    9.1: dict(week="w9", title="JavaDoc and Documentation",
             concepts=["Documentation", "Code Style", "API Usage"],
             visual="粉笔打开的书（书页留白），书页上方一个对话框气泡，旁边一个空白便签框",
             next_lecture="并发：线程与共享数据"),
    25: dict(week="w9", title="Concurrency: Thread, Runnable and Shared Data",
             concepts=["Threads and Concurrency", "Code Style"],
             visual="两条平行的粉笔铁轨（各自一个小方块在跑），中间一个交叉点的警示标志，一个空白气泡",
             next_lecture="标准 Java 类库与 JAR"),
    26: dict(week="w9", title="Standard Java Libraries and JAR",
             concepts=["API Usage", "Documentation", "Code Style"],
             visual="一个粉笔工具箱（打开盖），里面三件工具线稿，旁边一个空白标签框和一个空白气泡",
             next_lecture=None),
}

STYLE = ("墨绿色黑板背景，白色粉笔手绘线条，笔触带轻微手绘不完美感；黄色/蓝色粉笔只做少量点缀；"
         "画面大量留黑不要填满；绝对禁止任何文字、字母、数字、汉字笔画、似字纹理；"
         "所有「空白」区域必须是完全空白的气泡/便签/线框。16:9 横版。")


def board_prompts(lec: dict, n: int) -> list[str]:
    """n 号场 → 板图 prompt。统一布局：主体在左 2/3，右侧一个空白气泡或方框。"""
    subject = lec["visual"]
    layouts = [
        f"画面：{subject}。主体上方悬挂一盏小吊灯线稿，右下角一个空白长方形粉笔框。",
        f"画面：{subject}。左侧一个空白对话气泡（完全空白），主体与气泡之间一条黄色粉笔虚线。",
        f"画面：{subject}。主体右侧一个空白大长方框（完全空白），一条蓝色粉笔箭头从主体指向方框。",
        f"画面：{subject}。主体下方一条黄色粉笔下划线，右上角一个空白小气泡。",
        f"画面：{subject}。主体左上角一颗黄色粉笔星，右侧一个空白长方形框。",
        f"画面：{subject}。主体与右侧一个空白便签框之间画一个蓝色加号，便签框完全空白。",
        f"画面：{subject}。主体上方一条黄色弧线装饰，下方一个空白横条框。",
        f"画面：{subject}。右下角一个大号向右粉笔箭头，箭头末端一个空白方框。",
    ]
    return [f"画一张黑板风插画：{STYLE}\n{layouts[i % len(layouts)]}" for i in range(n)]


def scenes_for(num: int, lec: dict, concepts: dict, course: str, course_title: str) -> list[dict]:
    """8 场：片头/问题/概念×3/陷阱/例子/总结。全部文本取自 IR 概念记录。"""
    cdefs = []
    for cname in lec["concepts"]:
        c = concepts.get(cname)
        if not c:
            continue
        cdefs.append({
            "name": cname,
            "definition": c["definition"],
            "why": c["why"],
            "failure": (c.get("failure_conditions") or [""])[0],
            "example": c.get("example", ""),
        })
    while len(cdefs) < 3:
        cdefs.append(cdefs[-1])

    pitfalls = json.loads((REPO / "docs/courses/cs106a/course_ir.json").read_text())
    week = next(w for w in pitfalls["weeks"] if w["id"] == lec["week"])
    pit = week["pitfalls"]
    q = week["question"]
    title_zh = lec["title"]

    def S(sid, img, caption, boxes):
        return {"scene_id": sid, "image": img, "pause_seconds": 0,
                "caption": caption, "boxes": boxes}

    def box(bid, text, x, y, w, h, size, color, align="left", stage=1, role="body"):
        return {"box_id": bid, "text": text, "role": role, "font_size": size,
                "color": color, "align": align, "background": "transparent", "stage": stage,
                "rect_1920x1080_px": {"x": x, "y": y, "w": w, "h": h}}

    W, Y, B = "#F5F4E8", "#F6D87F", "#97D9F5"
    scenes = []

    # s01 片头：大框布局（同 L01 s01 的板图布局约定：右上空白框放标题区）
    scenes.append(S("s01", "boards/cs106a_s01.png",
        f"{course} 第 {num:g} 讲：{title_zh}。这一讲回答一个问题的第一步：{q}",
        [box("title", f"第 {num:g} 讲 · {title_zh}", 480, 360, 980, 100, 64, W, role="title"),
         box("sub", f"斯坦福 {course} · 编程方法论", 484, 500, 900, 64, 38, B),
         box("hook", lec["concepts"][0], 484, 640, 760, 72, 44, Y)]))

    # s02 本讲问题（用 s02 板图布局：门内气泡 + 三卡片 + 底部事实条）
    scenes.append(S("s02", "boards/cs106a_s02.png",
        f"为什么这门课要把「{lec['concepts'][0]}」放在这一讲？{week['why']}理解了它，后面所有的内容都挂在它上面。",
        [box("q", "这一讲\n讲什么？", 460, 380, 260, 130, 34, Y, align="center"),
         box("c1", lec["concepts"][0][:7], 1160, 450, 170, 200, 30, W, align="center"),
         box("c2", lec["concepts"][1][:7], 1385, 450, 180, 200, 30, W, align="center"),
         box("c3", lec["concepts"][2][:7], 1610, 450, 180, 200, 30, W, align="center"),
         box("fact", week["why"][:24], 120, 920, 900, 66, 34, B)]))

    # s03-s05 三个概念（同一张 s03 板图布局：屏幕=概念名，气泡=为什么，右框=失败条件）
    for i, c in enumerate(cdefs[:3]):
        scenes.append(S(f"s0{3+i}", "boards/cs106a_s03.png",
            f"核心概念{i+1}：{c['name']}。{c['definition']}它的价值在于：{c['why']}",
            [box("name", c["name"][:6], 190, 560, 330, 100, 54, W, align="center", role="celltitle"),
             box("why", "为什么：\n" + c["why"][:14], 690, 400, 400, 90, 38, Y, align="center"),
             box("fail", "失败条件：\n" + c["failure"][:16], 1370, 380, 420, 140, 34, B, align="center")]))

    # s06 陷阱（s06 板图布局：卷轴三行 + 右侧气泡）
    scenes.append(S("s06", "boards/cs106a_s06.png",
        f"这一讲最常见的三个坑：{'；'.join(pit[:3])}。避开它们，作业就成功了大半。",
        [box("title", "常见陷阱", 70, 70, 480, 92, 60, Y, role="title"),
         box("rule", f"一、{pit[0]}\n二、{pit[1]}\n三、{pit[2]}", 740, 450, 480, 260, 40, W, align="center"),
         box("note", "作业扣分重灾区", 1580, 250, 250, 150, 32, B, align="center")]))

    # s07 例子（s07 板图布局：左右气泡夹主体）
    ex = cdefs[0]
    scenes.append(S("s07", "boards/cs106a_s07.png",
        f"放到例子里看：{ex['example']}。概念只有落在这样的任务里，才真正变成你的能力。",
        [box("title", "动手例子", 70, 70, 480, 92, 60, Y, role="title"),
         box("inp", "任务\n输入", 170, 480, 240, 200, 40, W, align="center"),
         box("out", ex["example"][:10], 1530, 400, 260, 280, 38, W, align="center")]))

    # s08 总结与下讲预告（s08 板图布局：左框→箭头→右框）
    nxt = lec.get("next_lecture") or "课程完结"
    scenes.append(S("s08", "boards/cs106a_s08.png",
        f"这一讲我们拿下了 {lec['concepts'][0]}、{lec['concepts'][1]} 和 {lec['concepts'][2]}。下一讲：{nxt}。斯坦福 {course}，下节课见。",
        [box("you", "本讲", 460, 690, 230, 200, 60, W, align="center", role="celltitle"),
         box("next", "下一讲", 1240, 500, 340, 120, 44, Y, align="center"),
         box("karel", nxt[:6], 1670, 470, 200, 180, 44, W, align="center", role="celltitle")]))

    return scenes


def main():
    num = float(sys.argv[1])
    if num.is_integer():
        num = int(num)
    key = num
    lec = LECTURES[key]
    course = "CS106A"

    ir = json.loads((REPO / "docs/courses/cs106a/course_ir.json").read_text())
    concepts = json.loads((REPO / "docs/courses/cs106a/concepts.json").read_text())
    course_title = ir["title"]

    series = f"cs106a_l{num:g}".replace(".", "p")
    scenes = scenes_for(num, lec, concepts, course, course_title)

    pack = {
        "schema_version": "1.0",
        "course": f"{course} Lecture {num:g} · {lec['title']}（SEE Java 版）",
        "board_basis": "1672x941 源图，槽位坐标为 rect_1920x1080_px",
        "scenes": scenes,
    }
    out = ROOT / f"{series}_video"
    (out / "narration").mkdir(parents=True, exist_ok=True)
    (out / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "narration/all.json").write_text(
        json.dumps({s["scene_id"]: s["caption"] for s in scenes}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    prompts = board_prompts(lec, 3)  # s03 布局复用给 s03-s05，只需 3 张新图
    (out / "board_prompts.json").write_text(
        json.dumps({"series": series, "prompts": prompts}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    total = sum(len(s["caption"]) for s in scenes)
    print(f"{series}: {len(scenes)} 场 / {sum(len(s['boxes']) for s in scenes)} 框 / 旁白 {total} 字 ≈ {total//4}s")
    print(f"  -> {out/'pack.json'}")
    print(f"  板图：s01/s02/s06/s07/s08 复用 L01 已有布局图；s03 布局图 3 张（每讲主体不同）→ 交给 Gemini 循环")


if __name__ == "__main__":
    main()
