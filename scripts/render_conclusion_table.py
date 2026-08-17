#!/usr/bin/env python3
"""把一份诊断结论表渲染成一张 Geometry Blue 表格画板（示例用）。

固定示例数据，展示结论表的三列 × 四行结构，供 README 呈现。
Geometry Blue 风格：白底、黑线、单一蓝色强调 #2F6BFF。
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path

W, H = 1240, 900
BLACK = "#111111"
GRAY = "#666666"
MUTED = "#8A8A8A"
LIGHT = "#E8E8E8"
HEAD = "#F2F5FF"
FILL = "#F7F7F7"
BLUE = "#2F6BFF"
WARN = "#E0574A"
FONT = "-apple-system,BlinkMacSystemFont,'PingFang SC','Noto Sans CJK SC',sans-serif"


def esc(v): return html.escape(str(v), quote=True)


def txt(x, y, v, size=15, fill=BLACK, anchor="start", weight=400):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}px" font-weight="{weight}" fill="{fill}">{esc(v)}</text>')


def multiline(x, y, lines, size=13, fill=GRAY, lh=23, weight=400):
    out = []
    for i, ln in enumerate(lines):
        out.append(txt(x, y + i * lh, ln, size, fill, weight=weight))
    return "".join(out)


# 示例诊断数据（与 diagnose.py 对 case-achievement 的输出一致）
ROWS = [
    {
        "dim": "你被什么驱动",
        "result": ["主导是成就需要，其次是权力/", "影响需要，亲和需要偏弱。"],
        "ev": [
            "1. 成就（强）：OKR 定了「从零搭建",
            "   监控体系」拉伸目标；5000 字复盘",
            "2. 权力（中）：牵头跨团队专项，",
            "   协调三个组",
        ],
    },
    {
        "dim": "你现在的状态",
        "result": ["归属 偏低；自主、胜任 尚可。"],
        "ev": [
            "1. 归属（偏低）：较少参与团队活动，",
            "   多为独立作战",
            "2. 自主（尚可）：自主设定拉伸目标",
            "3. 胜任（尚可）：写了 5000 字复盘",
        ],
    },
    {
        "dim": "这意味着什么",
        "highlight": True,
        "result": ["想要的是「成就」，但当前「归属」", "偏低——方向对，动力却在流失，", "这是最该优先补的地方。"],
        "ev": [
            "1. 从「搞定难事」本身获得满足，",
            "   不是靠钱或头衔",
            "2. 团队连接偏弱、孤军奋战，",
            "   时间长了动力会被磨掉",
        ],
    },
    {
        "dim": "所以该怎么办",
        "result": ["把机会给对，同时补上偏低的需求。"],
        "ev": [
            "1. 争取有难度、能拉伸的项目，",
            "   让成果被看见",
            "2. 补团队连接、别让 TA 长期",
            "   孤军奋战",
        ],
    },
]


def build() -> str:
    b = []
    b.append(txt(60, 58, "员工动机诊断 · 结论表", 27, BLACK, weight=700))
    b.append(txt(60, 88, "一条逻辑线：被什么驱动 → 现在的状态 → 这意味着什么 → 所以该怎么办", 14, GRAY))

    # 表格布局
    x0, y0 = 60, 120
    col = [190, 430, 560]  # 列宽：诊断维度 / 诊断结果 / 支撑论据
    cx = [x0, x0 + col[0], x0 + col[0] + col[1]]
    table_w = sum(col)
    head_h = 44
    row_h = 150

    # 表头
    b.append(f'<rect x="{x0}" y="{y0}" width="{table_w}" height="{head_h}" fill="{HEAD}" />')
    heads = ["诊断维度", "诊断结果（大白话）", "支撑论据（来自飞书 / Agent 交流）"]
    for i, h in enumerate(heads):
        b.append(txt(cx[i] + 20, y0 + 29, h, 15, BLUE, weight=700))

    # 行
    y = y0 + head_h
    for ri, row in enumerate(ROWS):
        if row.get("highlight"):
            b.append(f'<rect x="{x0}" y="{y}" width="{table_w}" height="{row_h}" fill="{FILL}" />')
        # 维度列
        b.append(txt(cx[0] + 20, y + 40, row["dim"], 16, BLACK, weight=700))
        if row.get("highlight"):
            b.append(txt(cx[0] + 20, y + 68, "▲ 关键", 12, BLUE, weight=600))
        # 结果列
        b.append(multiline(cx[1] + 20, y + 36, row["result"], 14, BLACK, 24, weight=500))
        # 论据列
        b.append(multiline(cx[2] + 20, y + 34, row["ev"], 12.5, GRAY, 22))
        y += row_h

    # 边框与网格
    total_h = head_h + row_h * len(ROWS)
    b.append(f'<rect x="{x0}" y="{y0}" width="{table_w}" height="{total_h}" fill="none" stroke="{BLACK}" stroke-width="1.5" />')
    # 竖线
    for c in cx[1:]:
        b.append(f'<line x1="{c}" y1="{y0}" x2="{c}" y2="{y0 + total_h}" stroke="{LIGHT}" stroke-width="1" />')
    # 横线
    yy = y0 + head_h
    for _ in range(len(ROWS)):
        b.append(f'<line x1="{x0}" y1="{yy}" x2="{x0 + table_w}" y2="{yy}" stroke="{LIGHT}" stroke-width="1" />')
        yy += row_h

    # 脚注
    fy = y0 + total_h + 34
    b.append(txt(60, fy, "诊断结果是大白话总结；支撑论据用 1. 2. 3. 分条，均可回溯到飞书资产或与 Agent 的交流。", 13, MUTED))
    b.append(txt(60, fy + 24, "行为不完全等于动机，结论为推断，最终需本人确认。", 13, MUTED))

    body = "".join(b)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'  <rect width="{W}" height="{H}" fill="#FFFFFF" />\n  {body}\n</svg>\n')


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="assets/boards/5-conclusion-table.svg")
    a = p.parse_args(argv)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(build(), encoding="utf-8")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
