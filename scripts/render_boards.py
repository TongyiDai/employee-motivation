#!/usr/bin/env python3
"""渲染员工动机诊断的四张 Geometry Blue 画板。"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

W, H = 1200, 675
BLACK = "#111111"
LINE = "#222222"
GRAY = "#666666"
GUIDE = "#B8B8B8"
LIGHT = "#E8E8E8"
FILL = "#F5F5F5"
BLUE = "#2F6BFF"
FONT = "-apple-system,BlinkMacSystemFont,'PingFang SC','Noto Sans CJK SC',sans-serif"


def esc(v): return html.escape(str(v), quote=True)


def txt(x, y, v, size=16, fill=BLACK, anchor="middle", weight=400, letter=0):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}px" font-weight="{weight}" letter-spacing="{letter}px" fill="{fill}">{esc(v)}</text>')


def two_lines(x, y, a, b, size=16, fill=BLACK, gap=20, weight=600):
    return txt(x, y - gap/2 + 5, a, size, fill, weight=weight) + txt(x, y + gap/2 + 5, b, size, fill, weight=weight)


def line(x1, y1, x2, y2, color=LINE, width=1.5, arrow=False, dashed=False):
    m = ' marker-end="url(#arrow)"' if arrow else ""
    d = ' stroke-dasharray="5 7"' if dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d}{m} />'


def rect(x, y, w, h, fill="none", stroke=LINE, width=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" />'


def circle(cx, cy, r, fill="none", stroke=LINE, width=1.5):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" />'


def title(scene):
    it = scene["intent"]
    return "".join([
        txt(96, 78, it["core_message"], 32, BLACK, "start", 650),
        txt(96, 108, it.get("subtitle", ""), 14, GRAY, "start"),
        line(96, 136, 1104, 136, LIGHT, 1),
    ])


# ---------- 1：双模型骨架 方向×状态 ----------
def render_dual(scene):
    b = [title(scene)]
    # 左块：麦氏方向
    b.append(rect(120, 210, 420, 300, FILL, "none", 0))
    b.append(txt(330, 246, "麦克利兰三需要 · 方向", 15, GRAY, weight=600))
    b.append(txt(330, 270, "被什么驱动", 12, GRAY))
    for i, (zh, en) in enumerate([("成就", "想把事做到最好"), ("亲和", "想要关系与归属"), ("影响", "想影响与推动")]):
        y = 312 + i * 58
        b.append(rect(156, y - 26, 348, 46, "#FFFFFF", LINE, 1.4))
        b.append(txt(180, y, zh, 17, BLACK, "start", 650))
        b.append(txt(250, y, en, 13, GRAY, "start"))
    # 右块：SDT 状态
    b.append(rect(660, 210, 420, 300, "#FFFFFF", LIGHT, 1))
    b.append(txt(870, 246, "自我决定理论 SDT · 状态", 15, GRAY, weight=600))
    b.append(txt(870, 270, "被满足了没", 12, GRAY))
    for i, (zh, en) in enumerate([("自主", "自己决定、认同"), ("胜任", "有能力、在变强"), ("归属", "被连接、被在意")]):
        y = 312 + i * 58
        b.append(rect(696, y - 26, 348, 46, "#FFFFFF", LINE, 1.4))
        b.append(txt(720, y, zh, 17, BLUE, "start", 650))
        b.append(txt(788, y, en, 13, GRAY, "start"))
    # 中间 × 连接
    b.append(circle(600, 360, 30, BLUE))
    b.append(txt(600, 368, "×", 30, "#FFFFFF", weight=700))
    b.append(txt(600, 556, "方向 × 状态 = 立体诊断，而非贴标签", 14, GRAY))
    return "".join(b)


# ---------- 2：飞书资产 → 六维度 → 证据链 ----------
def render_evidence(scene):
    b = [title(scene)]
    assets = ["OKR", "员工文档", "周会表现", "与 Agent 的交流", "对话消息(辅助)"]
    for i, a in enumerate(assets):
        y = 210 + i * 54
        b.append(rect(110, y - 22, 190, 40, "#FFFFFF", LINE, 1.3))
        b.append(txt(205, y + 4, a, 14, BLACK, weight=600))
        b.append(line(300, y - 2, 452, y - 2, GUIDE, 1.2, arrow=True))
    # 中心：诊断引擎
    b.append(circle(540, 330, 62, BLUE))
    b.append(two_lines(540, 327, "双模型", "诊断", 18, "#FFFFFF", 22, 650))
    # 输出：证据链卡
    b.append(line(602, 330, 700, 330, LINE, 1.5, arrow=True))
    b.append(rect(716, 214, 372, 232, "#FFFFFF", LINE, 1.5))
    b.append(txt(902, 250, "每条结论带证据链", 15, BLACK, weight=650))
    for i, t in enumerate(["维度：倾向强/中/弱", "├ 支撑证据：哪个资产的哪条行为", "├ 推断逻辑：为什么指向这个维度", "└ 置信度 + 需本人确认"]):
        b.append(txt(740, 292 + i * 34, t, 14, GRAY if i else BLUE, "start", 600 if i == 0 else 400))
    b.append(txt(600, 556, "行为不完全等于动机，结论为推断，最终需本人确认", 13, GRAY))
    return "".join(b)


# ---------- 3：视角切换 ----------
def render_audience(scene):
    b = [title(scene)]
    # 中心：同一份诊断
    b.append(circle(600, 250, 46, BLUE))
    b.append(two_lines(600, 247, "同一份", "诊断", 15, "#FFFFFF", 20, 650))
    # 左：自测
    b.append(rect(140, 380, 420, 150, FILL, LINE, 1.4))
    b.append(txt(350, 414, "员工自测 · 员工视角", 16, BLACK, weight=650))
    for i, t in enumerate(["你的主导动机是什么", "当前哪个需求没被满足", "未来该争取什么机会、补哪一块"]):
        b.append(txt(168, 448 + i * 26, "· " + t, 13, GRAY, "start"))
    # 右：他评
    b.append(rect(640, 380, 420, 150, "#FFFFFF", LINE, 1.4))
    b.append(txt(850, 414, "Leader/HR 他评 · 管理视角", 16, BLUE, weight=650))
    for i, t in enumerate(["该成员被什么驱动", "该给他分什么活、怎么激励", "团队缺哪种驱动、怎么补位"]):
        b.append(txt(668, 448 + i * 26, "· " + t, 13, GRAY, "start"))
    b.append(line(560, 300, 360, 378, LINE, 1.5, arrow=True))
    b.append(line(640, 300, 840, 378, LINE, 1.5, arrow=True))
    b.append(txt(600, 588, "他评仅限直属成员、且过程对本人透明可复核", 13, GRAY))
    return "".join(b)


# ---------- 4：隐私边界 ----------
def render_boundary(scene):
    b = [title(scene)]
    b.append(rect(112, 196, 476, 340, FILL, "none", 0))
    b.append(rect(706, 196, 382, 340, "#FFFFFF", LIGHT, 1))
    b.append(line(647, 190, 647, 548, GUIDE, 1, dashed=True))
    b.append(txt(350, 228, "用来", 15, GRAY, weight=600))
    b.append(txt(897, 228, "明确拒绝", 15, GRAY, weight=600))
    b.append(circle(250, 320, 40, "#FFFFFF", LINE, 1.5))
    b.append(f'<circle cx="250" cy="320" r="8" fill="{BLUE}" />')
    b.append(txt(250, 388, "帮人更懂自己", 14, BLACK, weight=600))
    b.append(txt(250, 410, "帮管理者把机会给对", 14, BLACK, weight=600))
    b.append(line(330, 320, 420, 320, LINE, 1.5, arrow=True))
    b.append(rect(432, 288, 120, 64, "#FFFFFF", LINE, 1.4))
    b.append(txt(492, 316, "发展性对话", 13, BLACK, weight=600))
    b.append(txt(492, 338, "与授权安排", 13, BLACK, weight=600))
    for i, rj in enumerate(["性格标签", "绩效打分", "人员排序", "背对背画像"]):
        yy = 280 + i * 46
        b.append(txt(760, yy, "✕", 16, BLUE, "start", 700))
        b.append(txt(792, yy, rj, 16, GRAY, "start"))
    b.append(txt(350, 500, "行为为推断，最终解释权留给本人", 12, GRAY))
    b.append(txt(897, 500, "消息仅辅助、他评须透明", 12, GRAY))
    return "".join(b)


RENDERERS = {"dual": render_dual, "evidence": render_evidence,
             "audience": render_audience, "boundary": render_boundary}


def render(scene):
    fn = RENDERERS.get(scene["intent"]["composition"])
    if fn is None:
        raise ValueError(f"unsupported: {scene['intent']['composition']}")
    body = fn(scene)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>{esc(scene["intent"]["core_message"])}</title>
  <desc>Geometry Board for the 员工动机诊断 skill.</desc>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">
      <path d="M 0 0 L 8 4 L 0 8 z" fill="{LINE}" />
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="#FFFFFF" />
  {body}
</svg>
'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scene_dir", type=Path)
    p.add_argument("output_dir", type=Path)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    for sp in sorted(a.scene_dir.glob("*.json")):
        scene = json.loads(sp.read_text(encoding="utf-8"))
        out = a.output_dir / f"{sp.stem}.svg"
        out.write_text(render(scene), encoding="utf-8")
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
