#!/usr/bin/env python3
"""diagnose.py 的单元测试。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "diagnose.py"
FIX = ROOT / "tests" / "fixtures"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def test_primary_driver_detected():
    r = run("--input", str(FIX / "case-achievement.json"), "--format", "json")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["primary"] == "achievement"


def test_evidence_chain_present():
    r = run("--input", str(FIX / "case-achievement.json"), "--audience", "self", "--format", "markdown")
    assert "支撑证据" in r.stdout
    assert "推断逻辑" in r.stdout
    assert "置信度" in r.stdout


def test_self_vs_manager_advice_differs():
    s = run("--input", str(FIX / "case-achievement.json"), "--audience", "self", "--format", "markdown").stdout
    m = run("--input", str(FIX / "case-achievement.json"), "--audience", "manager", "--format", "markdown").stdout
    # self 建议里有「争取」，manager 建议里有「给他」
    assert "争取" in s
    assert "给他" in m


def test_dual_model_sections():
    r = run("--input", str(FIX / "case-achievement.json"), "--format", "markdown")
    assert "麦克利兰三需要" in r.stdout
    assert "自我决定理论 SDT" in r.stdout


def test_sdt_low_signal_surfaces():
    r = run("--input", str(FIX / "case-achievement.json"), "--format", "json")
    out = json.loads(r.stdout)
    assert out["sdt_low"]["relatedness"] >= 1


def test_reject_pii():
    r = run("--input", str(FIX / "invalid-pii.json"))
    assert r.returncode == 2
    assert "隐私边界" in r.stderr


def test_team_missing_driver():
    r = run("--team", str(FIX / "team.json"), "--format", "markdown")
    assert r.returncode == 0
    assert "亲和需要" in r.stdout  # team.json 缺亲和型


def test_confidence_high_with_three_evidence():
    r = run("--input", str(FIX / "case-achievement.json"), "--audience", "self", "--format", "markdown")
    # 成就有 3 条证据，置信度应为高
    assert "置信度：高" in r.stdout


def test_summary_before_advice():
    r = run("--input", str(FIX / "case-achievement.json"), "--audience", "self", "--format", "markdown")
    out = r.stdout
    assert "## 总结" in out
    assert "## 建议" in out
    # 总结在建议之前
    assert out.index("## 总结") < out.index("## 建议")
    # 总结含驱动画像和 SDT 状态
    assert "动机状态（SDT）" in out


def test_agent_chat_evidence_counted():
    # fixture 里含「Agent 交流」来源的证据，应出现在证据链中
    r = run("--input", str(FIX / "case-achievement.json"), "--audience", "self", "--format", "markdown")
    assert "Agent 交流" in r.stdout


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} passed")
