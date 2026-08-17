#!/usr/bin/env python3
"""员工动机诊断（双模型：麦克利兰 nAch/nAff/nPow × SDT 自主/胜任/归属）。

输入一份脱敏的飞书证据 JSON（见 references/input-schema.md），
按证据把六个维度打分，输出带证据链和推断逻辑的诊断，并按 audience 切换建议视角。
含身份或敏感字段的输入一律拒绝。
"""

from __future__ import annotations

import argparse
import json
import re
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


def compact_observation(observation: str, limit: int = 34, summary: str | None = None) -> str:
    """把完整观察压成结论表里的短证据锚点；详情区仍保留原句。"""
    if summary and str(summary).strip():
        return str(summary).strip()
    text = " ".join(str(observation).split())
    match = re.search(r"在《([^》]+)》中，(.+?)(?:，并|；|。|，本人|$)", text)
    if match:
        title, action = match.groups()
        action = action.rstrip("，。；")
        if len(action) > limit:
            action = action[:limit].rstrip("，、；") + "…"
        return f"《{title}》：{action}"
    if len(text) > limit:
        return text[:limit].rstrip("，、；") + "…"
    return text


def short_evidence(hits: list[dict], label: str | None = None, limit: int = 2) -> list[str]:
    """结论表专用：来源 + 短行为锚点，不把详情搬进总览。"""
    rows = []
    for h in hits[:limit]:
        prefix = f"{label}｜" if label else ""
        rows.append(f"{prefix}{h['source']}：{compact_observation(h['observation'], summary=h.get('summary'))}")
    return rows


def diagnose_person(data: dict, model: dict) -> dict:
    evidence = data.get("evidence", [])
    mcc_hits = {k: [] for k in MCC}
    sdt_hits = {k: [] for k in SDT}
    sdt_low = {k: [] for k in SDT}

    for ev in evidence:
        for sig in ev.get("signals", []):
            item = {
                "source": ev.get("source", "?"),
                "observation": ev.get("observation", ""),
                "summary": ev.get("summary", ""),
            }
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
        if low_hits is None:
            L.append("- 替代解释/需确认：也可能来自岗位要求或当期项目阶段；需本人确认是否有内在投入。")
        else:
            L.append("- 不能由行为证明：现有记录能说明工作方式，不能单独证明主观满足感；需本人确认。")
    else:
        L.append("- 证据不足：现有飞书资产未见明显信号，暂不下结论。")
    if low_hits:
        L.append(f"- ⚠ 低满足信号：")
        for h in low_hits:
            L.append(f"  - [{h['source']}] {h['observation']}")
    return L


def _anchor(hits: list[dict], fallback: str) -> str:
    """把证据压成行动锚点，保留真实场景，避免建议漂浮。"""
    if not hits:
        return fallback
    text = " ".join(str(hits[0].get("observation", "")).split())
    return text[:140] + ("…" if len(text) > 140 else "")


def _scene(ctx: dict, key: str, hits: list[dict], fallback: str) -> str:
    """优先使用 Agent 从证据归纳的短场景名，再回退到原始观察。"""
    scenes = ctx.get("action_scenes", {})
    if isinstance(scenes, dict) and isinstance(scenes.get(key), str) and scenes[key].strip():
        return scenes[key].strip()
    return _anchor(hits, fallback)


def render_concrete_actions(data: dict, r: dict, model: dict, audience: str) -> list[str]:
    """从真实证据改写行动；没有场景时明确标记待补，不凭空造项目。"""
    ctx = data.get("context", {})
    role = ctx.get("role", "当前工作")
    scenario = ctx.get("scenario") or f"{role}中的当前重点工作"
    subj = "你" if audience == "self" else "TA"
    mcc = model["mcclelland"]["needs"]
    sdt = model["sdt"]["needs"]
    actions: list[dict[str, str]] = []

    if r["primary"]:
        key = r["primary"]
        anchor = _scene(ctx, key, r["mcc_hits"][key], scenario)
        if audience == "self":
            action = (f"把“{anchor}”选为一个端到端主战场，下一次复盘前写清一个结果指标、一个质量或验收标准，"
                      "并约定完成日期。")
            boundary = "先写清本人可决定的事项、需要他人配合的事项和最终验收人。"
        else:
            action = (f"把“{anchor}”整理成一块完整责任域交给 TA，明确结果指标、质量或验收标准，"
                      "并在下一次复盘前确认完成日期。")
            boundary = "给 TA 对做法的选择权，同时明确需要谁配合和谁验收。"
        actions.append({
            "title": f"把{mcc[key]['label']}放进一个可验收的主战场",
            "scene": anchor,
            "action": action,
            "result": "交付物、指标、质量阈值和完成日期可被复盘，不用“做好了”作结论。",
            "time": "下一次项目复盘或一个工作周期内",
            "boundary": boundary,
            "review": "若指标或验收标准无法写清，先缩小范围并补一次 1:1 核实。",
        })

    if r["mcc_hits"]["power"]:
        anchor = _scene(ctx, "power", r["mcc_hits"]["power"], scenario)
        if audience == "self":
            action = (f"在“{anchor}”对应的跨团队事项中，把推动事项改写成 owner、截止时间和决策点，"
                      "每次会议只保留未关闭的阻塞项。")
        else:
            action = (f"在“{anchor}”对应的跨团队事项中，给 TA 一个明确的牵头范围，"
                      "要求会议产出 owner、截止时间和决策点。")
        actions.append({
            "title": "把影响力落到决策点和责任人",
            "scene": anchor,
            "action": action,
            "result": "每个跨团队事项都有明确负责人、截止时间、决策点和验收结果。",
            "time": "下一次跨团队会议开始执行",
            "boundary": "区分本人能拍板的事项、需要上级拍板的事项和仅需同步的事项。",
            "review": "连续两次会议仍靠口头追踪时，停止追加协调，先补流程或权限。",
        })

    if r["mcc_hits"]["affiliation"]:
        anchor = _scene(ctx, "affiliation", r["mcc_hits"]["affiliation"], scenario)
        if audience == "self":
            action = (f"在“{anchor}”对应的协作场景中固定一个反馈回流节点：会前列问题、会后记负责人和期限，"
                      "下一次只复盘未关闭项。")
        else:
            action = (f"让 TA 在“{anchor}”对应的协作场景中负责一次结构化反馈回流，"
                      "会后保留负责人、期限和未关闭项。")
        actions.append({
            "title": "把协作连接变成稳定的反馈回路",
            "scene": anchor,
            "action": action,
            "result": "反馈有记录、有负责人、有期限，减少依赖个人记忆和碎片传话。",
            "time": "下一次访谈、评审或项目复盘",
            "boundary": "只承接本人能推动的反馈，不把所有协作问题都变成个人兜底。",
            "review": "若反馈连续两轮没有进入决策或产品改动，升级阻塞点或停止无效同步。",
        })

    for key in SDT:
        if r["sdt_low"][key]:
            anchor = _scene(ctx, key, r["sdt_low"][key], scenario)
            actions.append({
                "title": f"优先补足{ sdt[key]['label'] }需求",
                "scene": anchor,
                "action": {
                    "autonomy": "在下一轮任务分配前，先确认本人可选择的做法和认可的工作理由。",
                    "competence": "在下一轮任务分配前，把挑战拆成够得着的阶段，并约定成长反馈。",
                    "relatedness": "在下一次 1:1 或项目复盘中安排一次真实的双向反馈，不把连接等同于群消息。",
                }[key],
                "result": f"{sdt[key]['label']}需求有一个可观察的改善信号。",
                "time": "下一次 1:1、任务分配或项目复盘",
                "boundary": "只调整与该需求直接相关的工作条件，不把推断当作事实。",
                "review": "两次复盘后仍无改善时，回到本人确认问题是否判断错误。",
            })

    if not actions:
        actions.append({
            "title": "先补一个真实场景",
            "scene": "待补场景",
            "action": "请本人提供最近一件最有投入感和一件最消耗的工作，再据此改写行动。",
            "result": "至少获得一个可回溯的项目、会议或流程场景。",
            "time": "下一次 1:1 或诊断复核前",
            "boundary": "不在证据不足时编造项目、指标和期限。",
            "review": "补齐场景后重新运行诊断。",
        })

    L = ["## 具体下一步（贴合当前场景）", "",
         "> 以下动作从当前证据改写；时间、指标和责任边界仍需本人或负责人确认。", ""]
    for i, item in enumerate(actions[:5], 1):
        L.extend([
            f"### {i}. {item['title']}",
            f"- 真实场景：{item['scene']}",
            f"- 具体动作：{item['action']}",
            f"- 结果指标：{item['result']}",
            f"- 时间锚点：{item['time']}",
            f"- 决策/协作边界：{item['boundary']}",
            f"- 复盘触发：{item['review']}",
            "",
        ])
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

    # 结论表：三列（诊断维度 / 诊断结果 / 支撑论据）× 四行
    # 四行 = 被什么驱动 → 现在的状态 → 这意味着什么 → 所以该怎么办
    subj = "你" if audience == "self" else "TA"

    def numbered(items):
        return "<br>".join(f"{i}. {it}" for i, it in enumerate(items, 1) if it)

    L.append("## 结论表")
    L.append("")
    L.append("| 诊断维度 | 诊断结果 | 支撑论据 |")
    L.append("| --- | --- | --- |")

    # 行1：被什么驱动
    if prim:
        parts = [f"主导是{mcc[prim]['label']}"]
        if sec:
            parts.append(f"其次是{mcc[sec]['label']}")
        weakest = [k for k in MCC if len(r["mcc_hits"][k]) == 0]
        if weakest:
            parts.append("、".join(mcc[k]["label"] for k in weakest) + "偏弱")
        drive_result = "，".join(parts) + "。"
        drive_ev = []
        for k in MCC:
            hits = r["mcc_hits"][k]
            if hits:
                drive_ev.extend(short_evidence(hits, f"{mcc[k]['label']}（{tier(len(hits))}）", limit=1))
    else:
        drive_result = "现有证据不足以判断主导驱动，建议在 1:1 里核实。"
        drive_ev = ["暂无足够行为证据，建议补充 OKR、文档、周会或与 Agent 的交流记录"]
    L.append(f"| {subj}被什么驱动 | {drive_result} | {numbered(drive_ev)} |")

    # 行2：现在的状态
    lows = [k for k in SDT if r["sdt_low"][k]]
    goods = [k for k in SDT if len(r["sdt_hits"][k]) >= 1 and not r["sdt_low"][k]]
    if lows or goods:
        sp = []
        if lows:
            sp.append("、".join(sdt[k]["label"] for k in lows) + " 偏低")
        if goods:
            sp.append("、".join(sdt[k]["label"] for k in goods) + " 尚可")
        state_result = "；".join(sp) + "。"
        state_ev = []
        for k in lows:
            obs = r["sdt_low"][k][0]["observation"] if r["sdt_low"][k] else "该需求相关信号偏少"
            state_ev.extend(short_evidence(r["sdt_low"][k], f"{sdt[k]['label']}（偏低）", limit=1))
        for k in goods:
            state_ev.extend(short_evidence(r["sdt_hits"][k], f"{sdt[k]['label']}（尚可）", limit=1))
    else:
        state_result = "现有证据不足以判断动机状态。"
        state_ev = ["暂无足够状态信号，建议补充 1:1、协作、OKR 等资产"]
    L.append(f"| {subj}现在的状态 | {state_result} | {numbered(state_ev)} |")

    # 行3：这意味着什么（把驱动+状态的关系用大白话讲通）
    if prim and lows:
        mean_result = (f"{subj}想要的是「{mcc[prim]['label']}」那类的事，"
                       f"但当前「{'、'.join(sdt[k]['label'] for k in lows)}」偏低——"
                       f"方向对，动力却在流失，这是最该优先补的地方。")
        mean_ev = [mcc[prim]["implications"][0]] + [sdt[k]["low_implications"][0] for k in lows]
    elif prim:
        mean_result = f"{subj}被「{mcc[prim]['label']}」驱动，且几项状态都还不错，方向与状态匹配良好。"
        mean_ev = [mcc[prim]["implications"][0]] + [sdt[k]["good_implication"] for k in goods[:2]]
    else:
        mean_result = "方向和状态都还不清楚，先补证据再谈关系。"
        mean_ev = ["动机是推断，不是标签；证据不足时不硬下结论"]
    L.append(f"| 这意味着什么 | {mean_result} | {numbered(mean_ev)} |")

    # 行4：所以该怎么办
    key = "self_advice" if audience == "self" else "manager_advice"
    todo = []
    if prim:
        todo.append(mcc[prim][key].rstrip("。"))
    for k in lows:
        fix = {"autonomy": "减少微观管理、给自主决定的空间",
               "competence": "给够得着的挑战和及时的成长反馈",
               "relatedness": f"补团队连接、别让{subj}长期孤军奋战"}[k]
        todo.append(fix)
    if not todo:
        todo = ["先在 1:1 里核实动机与状态，再定动作"]
    todo_result = "把机会给对，同时补上偏低的需求。"
    L.append(f"| 所以该怎么办 | {todo_result} | {numbered(todo[:3])} |")
    L.append("")
    L.append(f"> 一条逻辑线：先看 {subj} 被什么驱动，再看现在状态如何，「这意味着什么」把两者的关系讲通，最后给出对应动作。诊断结果为大白话总结，支撑论据均来自飞书资产或与 Agent 的交流。下面是每个维度的完整证据链。")
    L.append("")
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

    L.extend(render_concrete_actions(data, r, model, audience))
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
