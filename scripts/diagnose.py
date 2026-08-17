#!/usr/bin/env python3
"""员工动机诊断（双模型：麦克利兰 nAch/nAff/nPow × SDT 自主/胜任/归属）。

输入一份脱敏的飞书证据 JSON（见 references/input-schema.md），
按证据把六个维度打分，输出带证据链和推断逻辑的诊断，并按 audience 切换建议视角。
含身份或敏感字段的输入一律拒绝。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "references" / "motivation-model.json"

FORBIDDEN_KEYS = {
    "姓名", "工号", "邮箱", "手机号", "身份证", "花名",
    "name", "employee_id", "email", "phone", "id_card",
    "salary", "薪酬", "薪资", "工资", "健康", "health",
    "家庭", "family", "年龄", "age", "性别", "gender", "民族", "宗教", "religion",
}

MCC = ["achievement", "affiliation", "power"]
SDT = ["autonomy", "competence", "relatedness"]
SDT_LOW = {"autonomy_low", "competence_low", "relatedness_low"}

LEVEL = [(0, "弱"), (1, "中"), (3, "强")]


def load_model() -> dict:
    with MODEL_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def scan_forbidden(obj, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS:
                hits.append(f"{path}.{k}" if path else k)
            hits.extend(scan_forbidden(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(scan_forbidden(v, f"{path}[{i}]"))
    return hits


def tier(score: int) -> str:
    label = "弱"
    for thr, name in LEVEL:
        if score >= thr:
            label = name
    return label


def confidence(n_evidence: int) -> str:
    return "高" if n_evidence >= 3 else "中" if n_evidence == 2 else "低"


def diagnose_person(data: dict, model: dict) -> dict:
    evidence = data.get("evidence", [])
    mcc_hits = {k: [] for k in MCC}
    sdt_hits = {k: [] for k in SDT}
    sdt_low = {k: [] for k in SDT}

    for ev in evidence:
        for sig in ev.get("signals", []):
            item = {"source": ev.get("source", "?"), "observation": ev.get("observation", "")}
            if sig in mcc_hits:
                mcc_hits[sig].append(item)
            elif sig in sdt_hits:
                sdt_hits[sig].append(item)
            elif sig in SDT_LOW:
                base = sig.replace("_low", "")
                if base in sdt_low:
                    sdt_low[base].append(item)

    mcc_scores = {k: len(v) for k, v in mcc_hits.items()}
    ranked = sorted(MCC, key=lambda k: -mcc_scores[k])
    primary = ranked[0] if mcc_scores[ranked[0]] > 0 else None
    secondary = ranked[1] if len(ranked) > 1 and mcc_scores[ranked[1]] > 0 else None

    return {
        "mcc_hits": mcc_hits, "sdt_hits": sdt_hits, "sdt_low": sdt_low,
        "mcc_scores": mcc_scores, "primary": primary, "secondary": secondary,
    }


def render_dimension(key, need, hits, low_hits=None) -> list[str]:
    L = []
    n = len(hits)
    L.append(f"### {need['label']}（{need['en']}）：倾向{tier(n)}")
    if n:
        L.append("- 支撑证据：")
        for h in hits:
            L.append(f"  - [{h['source']}] {h['observation']}")
        L.append(f"- 推断逻辑：以上行为符合「{need['label']}」的典型信号（{need['plain'][:24]}…）")
        L.append(f"- 置信度：{confidence(n)} —— 行为推断，与本人认知可能有差")
    else:
        L.append("- 证据不足：现有飞书资产未见明显信号，暂不下结论。")
    if low_hits:
        L.append(f"- ⚠ 低满足信号：")
        for h in low_hits:
            L.append(f"  - [{h['source']}] {h['observation']}")
    return L


def to_markdown(data: dict, r: dict, model: dict, audience: str) -> str:
    ctx = data.get("context", {})
    L = ["# 员工动机诊断", ""]
    who = " · ".join(x for x in [ctx.get("role"), ctx.get("tenure")] if x)
    if who:
        L.append(f"对象背景：{who}")
    L.append(f"视角：{'员工自测' if audience == 'self' else 'Leader/HR 他评'}")
    L.append("")
    L.append("> 本诊断基于飞书行为证据，采用麦克利兰三需要 × SDT 双模型。行为不完全等于动机，结论为推断，需本人确认。")
    L.append("")

    # 结论摘要（先总结）
    mcc = model["mcclelland"]["needs"]
    sdt = model["sdt"]["needs"]
    prim, sec = r["primary"], r["secondary"]
    L.append("## 总结")
    if prim:
        line = f"**主导驱动：{mcc[prim]['label']}**"
        if sec:
            line += f"　次要：{mcc[sec]['label']}"
        L.append(line)
        L.append("")
        # 一句话驱动画像
        who_word = "你" if audience == "self" else "TA"
        portrait = f"综合飞书行为证据，{who_word}最主要被「{mcc[prim]['label']}」驱动"
        if sec:
            portrait += f"，其次是「{mcc[sec]['label']}」"
        portrait += f"。{mcc[prim]['plain']}"
        L.append(portrait)
        # SDT 状态小结
        highs = [sdt[k]['label'] for k in SDT if len(r['sdt_hits'][k]) >= 1 and not r['sdt_low'][k]]
        lows = [sdt[k]['label'] for k in SDT if r['sdt_low'][k]]
        state_bits = []
        if highs:
            state_bits.append(f"当前满足较好的是：{'、'.join(highs)}")
        if lows:
            state_bits.append(f"可能未被满足、需要补的是：{'、'.join(lows)}")
        if state_bits:
            L.append("")
            L.append("动机状态（SDT）：" + "；".join(state_bits) + "。")
    else:
        L.append("现有证据不足以判断主导驱动，建议补充飞书资产（OKR、文档、周会、与 Agent 的交流）或在 1:1 核实。")
    L.append("")

    # 麦氏三需要
    L.append("## 驱动方向（麦克利兰三需要）")
    for k in MCC:
        L.extend(render_dimension(k, mcc[k], r["mcc_hits"][k]))
        L.append("")

    # SDT 三需求
    sdt = model["sdt"]["needs"]
    L.append("## 动机状态（自我决定理论 SDT）")
    for k in SDT:
        L.extend(render_dimension(k, sdt[k], r["sdt_hits"][k], r["sdt_low"][k]))
        L.append("")

    # 建议（按视角）
    L.append("## 建议")
    key = "self_advice" if audience == "self" else "manager_advice"
    if prim:
        L.append(f"**针对主导驱动「{mcc[prim]['label']}」：**")
        L.append(f"- {mcc[prim][key]}")
    for k in SDT:
        if r["sdt_low"][k]:
            hint = {"autonomy": "减少微观管理，给他对怎么做的选择权",
                    "competence": "任务与能力可能错配，给匹配挑战和成长反馈",
                    "relatedness": "创造真实的团队连接机会，别让他长期孤立"}[k]
            L.append(f"- SDT「{sdt[k]['label']}」满足度偏低：{hint}。")
    L.append("")
    L.append("详见 references/driver-actions.md。落地前先和本人确认。")
    L.append("")
    L.append("> 边界：本结论用于发展性对话与授权安排，不做性格标签、不进考核、不做背对背画像。")
    return "\n".join(L).rstrip() + "\n"


def team_markdown(data: dict, model: dict) -> str:
    mcc = model["mcclelland"]["needs"]
    members = data.get("members", [])
    dist = {k: 0 for k in MCC}
    for m in members:
        if m.get("primary") in dist:
            dist[m["primary"]] += 1
    L = [f"# 团队构成诊断：{data.get('team', '')}", ""]
    L.append(f"成员数：{len(members)}")
    L.append("")
    L.append("## 主导驱动分布")
    for k in MCC:
        L.append(f"- {mcc[k]['label']}：{dist[k]} 人")
    L.append("")
    missing = [mcc[k]['label'] for k in MCC if dist[k] == 0]
    L.append("## 补位提示")
    if missing:
        L.append(f"团队缺少：{'、'.join(missing)} 型驱动。")
        L.append(model["team_note"])
    else:
        L.append("三种驱动都有覆盖。保持平衡即可。")
    L.append("")
    L.append("> 团队视图只看驱动分布，用于补位，不对个人排优劣、不做评价。")
    return "\n".join(L).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="员工动机诊断（双模型）")
    parser.add_argument("--input", help="单人脱敏证据 JSON")
    parser.add_argument("--team", help="团队诊断 JSON")
    parser.add_argument("--audience", default="self", choices=["self", "manager"],
                        help="建议视角：self 员工自测 / manager 他评")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = parser.parse_args(argv)

    if not args.input and not args.team:
        parser.error("需提供 --input 或 --team")

    model = load_model()

    if args.team:
        with open(args.team, encoding="utf-8") as fh:
            data = json.load(fh)
        hits = scan_forbidden(data)
        if hits:
            print("错误：输入含身份或敏感字段，拒绝（隐私边界）。命中：" + "; ".join(hits[:6]), file=sys.stderr)
            return 2
        sys.stdout.write(team_markdown(data, model))
        return 0

    with open(args.input, encoding="utf-8") as fh:
        data = json.load(fh)
    hits = scan_forbidden(data)
    if hits:
        print("错误：输入含身份或敏感字段，拒绝（隐私边界）。命中：" + "; ".join(hits[:6]), file=sys.stderr)
        return 2

    # CLI 显式指定 --audience 时优先；否则用输入里的 context.audience；再否则默认
    audience = args.audience
    if "--audience" not in (argv if argv is not None else sys.argv):
        audience = data.get("context", {}).get("audience", args.audience)
    r = diagnose_person(data, model)
    if args.format == "json":
        out = {"primary": r["primary"], "secondary": r["secondary"], "mcc_scores": r["mcc_scores"],
               "audience": audience,
               "sdt_low": {k: len(v) for k, v in r["sdt_low"].items()}}
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(to_markdown(data, r, model, audience))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
