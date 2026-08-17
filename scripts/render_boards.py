#!/usr/bin/env python3
"""Render the public example boards for the employee-motivation skill."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

CREAM = "#fdf0e0"
BLUE = "#375dfe"
NAVY = "#1a2240"
WHITE = "#ffffff"
BLUE_LINE = "#2741c0"
FONT = "Noto Sans SC"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x: float, y: float, value: str, size: int = 24, fill: str = NAVY,
         anchor: str = "start", weight: int = 700) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-size="{size}" font-family="{FONT}" font-weight="{weight}" '
        f'fill="{fill}">{esc(value)}</text>'
    )


def rect(x: float, y: float, width: float, height: float, fill: str,
         stroke: str = "none", stroke_width: int = 0) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def board_header(core: str, subtitle: str, height: int = 200) -> str:
    return "".join([
        rect(0, 0, 1680, height, BLUE),
        text(70, 96, core, 58, CREAM),
        text(70, 166, subtitle, 30, CREAM),
    ])


def footer(value: str, y: int = 755) -> str:
    return "".join([
        rect(70, y, 1540, 55, CREAM, BLUE_LINE, 3),
        text(90, y + 36, value, 24, BLUE_LINE),
    ])


def render_dual(scene: dict) -> tuple[int, int, str]:
    b = [rect(0, 0, 1680, 960, CREAM), rect(0, 0, 620, 960, BLUE)]
    b.extend([
        text(70, 210, "双", 120, CREAM),
        text(70, 330, "模型", 120, CREAM),
        rect(70, 430, 490, 320, WHITE),
        text(102, 498, "麦克利兰 × SDT", 30),
        text(102, 548, "一个看驱动方向，", 30),
        text(102, 596, "一个看满足状态，", 30),
        text(102, 668, "一起看，才知道怎么给机会", 28, BLUE),
        text(700, 200, "一个问题：", 66),
        text(700, 288, "什么在驱动他？", 66),
        text(700, 376, "这股劲顺不顺？", 66, BLUE),
        rect(700, 430, 920, 290, BLUE),
        text(736, 510, "结论：方向 × 状态，", 40, CREAM),
        text(736, 566, "才是一份能指导工作的诊断。", 40, CREAM),
        text(736, 660, "成就 / 亲和 / 影响 × 自主 / 胜任 / 归属", 30, CREAM),
        rect(700, 770, 290, 140, BLUE, NAVY, 4),
        text(845, 840, "驱动方向", 32, CREAM, "middle"),
        rect(1010, 770, 290, 140, BLUE, NAVY, 4),
        text(1155, 840, "满足状态", 32, CREAM, "middle"),
        rect(1320, 770, 290, 140, WHITE, NAVY, 4),
        text(1465, 840, "发展行动", 32, BLUE, "middle"),
    ])
    return 1680, 960, "".join(b)


def render_evidence(scene: dict) -> tuple[int, int, str]:
    b = [rect(0, 0, 1680, 860, CREAM), board_header(
        scene["intent"]["core_message"], scene["intent"]["subtitle"])]
    b.extend([
        text(90, 235, "证据来源", 28),
        text(720, 235, "如何进入诊断", 28),
        text(1490, 235, "质量", 28, anchor="middle"),
    ])
    rows = [
        ("1 · 工作目标与文档", "目标、项目、交付物", "可追溯"),
        ("2 · 会议、周会与 Agent", "推进方式、决策与反馈", "可解释"),
        ("3 · 消息（仅作辅助）", "交叉验证，不单独定论", "需确认"),
    ]
    for i, (source, logic, quality) in enumerate(rows):
        y = 290 + i * 155
        b.extend([
            rect(70, y, 600, 130, WHITE, NAVY, 4),
            text(100, y + 55, source, 30),
            text(100, y + 100, "具体行为留下可回看的痕迹", 24, BLUE),
            rect(700, y, 720, 130, BLUE if i == 0 else CREAM, NAVY, 3),
            text(726, y + 55, logic, 26, CREAM if i == 0 else NAVY),
            text(726, y + 100, "映射维度 → 推断逻辑 → 置信度", 23, CREAM if i == 0 else NAVY),
            rect(1435, y, 175, 130, BLUE, NAVY, 4),
            text(1522, y + 78, quality, 30, CREAM, "middle"),
        ])
    return 1680, 860, "".join(b)


def render_audience(scene: dict) -> tuple[int, int, str]:
    b = [rect(0, 0, 1680, 860, CREAM), board_header(
        scene["intent"]["core_message"], scene["intent"]["subtitle"], 250),
        text(70, 325, "同一份证据，按使用者切换建议", 36)]
    cards = [
        (70, "01", "员工自测", "看发展", ["主导动机是什么", "哪个需求没被满足", "下一步争取什么机会"], False),
        (590, "02", "Leader / HR 他评", "看授权", ["该成员被什么驱动", "该分什么活、怎么激励", "团队缺哪种驱动"], False),
        (1110, "03", "共同底线", "透明可复核", ["成员知情", "证据可回看", "结论用于发展与授权"], True),
    ]
    for x, number, title, kicker, lines, blue_card in cards:
        fill = BLUE if blue_card else WHITE
        fg = CREAM if blue_card else NAVY
        accent = CREAM if blue_card else BLUE
        b.extend([
            rect(x, 385, 500, 315, fill, NAVY, 4),
            text(x + 35, 480, number, 80, accent),
            text(x + 35, 535, title, 30, fg),
            text(x + 35, 585, kicker, 26, accent),
            text(x + 35, 615, lines[0], 24, fg),
            text(x + 35, 655, lines[1], 24, fg),
            text(x + 35, 695, lines[2], 24, fg),
        ])
    b.append(footer("他评只对直属成员开放，过程对本人透明可复核。"))
    return 1680, 860, "".join(b)


def render_boundary(scene: dict) -> tuple[int, int, str]:
    b = [rect(0, 0, 1680, 860, CREAM), board_header(
        scene["intent"]["core_message"], scene["intent"]["subtitle"], 250),
        text(70, 325, "诊断用于把机会给对，也用于守住人的边界", 36)]
    cards = [
        (70, "01", "发展对话", ["主导动机", "满足状态", "下一步机会"], False),
        (590, "02", "透明可复核", ["本人知情", "证据可回看", "保留替代解释"], False),
        (1110, "03", "明确拒绝", ["性格标签", "绩效打分", "人员排序 / 背对背画像"], True),
    ]
    for x, number, title, lines, blue_card in cards:
        fill = BLUE if blue_card else WHITE
        fg = CREAM if blue_card else NAVY
        accent = CREAM if blue_card else BLUE
        b.extend([
            rect(x, 385, 500, 315, fill, NAVY, 4),
            text(x + 35, 480, number, 80, accent),
            text(x + 35, 535, title, 30, fg),
            text(x + 35, 595, lines[0], 26, fg),
            text(x + 35, 645, lines[1], 26, fg),
            text(x + 35, 695, lines[2], 24, fg),
        ])
    b.append(footer("行为是动机线索；主观感受仍需本人确认，结论用于发展与授权。"))
    return 1680, 860, "".join(b)


RENDERERS = {
    "dual": render_dual,
    "matrix-2d": render_dual,
    "evidence": render_evidence,
    "input-process-output": render_evidence,
    "audience": render_audience,
    "radial-center": render_audience,
    "boundary": render_boundary,
    "tension-contrast": render_boundary,
}


def render(scene: dict) -> str:
    renderer = RENDERERS.get(scene["intent"]["composition"])
    if renderer is None:
        raise ValueError(f"unsupported composition: {scene['intent']['composition']}")
    width, height, body = renderer(scene)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <title>{esc(scene["intent"]["core_message"])}</title>
  <desc>Editable Geometry Blue board for the employee-motivation skill.</desc>
  {body}
</svg>
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scene_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for scene_path in sorted(args.scene_dir.glob("*.json")):
        scene = json.loads(scene_path.read_text(encoding="utf-8"))
        output = args.output_dir / f"{scene_path.stem}.svg"
        output.write_text(render(scene), encoding="utf-8")
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
