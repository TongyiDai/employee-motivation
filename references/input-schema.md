# 输入格式规范

`diagnose.py` 的输入是一份**脱敏**的证据 JSON，由飞书数据资产整理而来。不含姓名、工号等身份标识，也不含敏感个人信息。

## 单人诊断输入

```json
{
  "context": {
    "role": "高级工程师",
    "tenure": "2 年",
    "audience": "self",
    "scenario": "当前主要工作场景，可脱敏；没有时由 Agent 从 evidence 归纳",
    "action_scenes": {
      "achievement": "People/HR AI 工作流自动化：端到端流程",
      "power": "跨团队项目：决策点与规模化",
      "affiliation": "客户/CSM/研发协作：反馈回流"
    },
    "output": {
      "detail": "full",
      "feishu_doc": false,
      "geometry_board": false
    },
    "note": "audience: self（员工自测）/ manager（Leader/HR 他评）"
  },
  "evidence": [
    {"source": "OKR", "observation": "本季度给自己定了从零搭建监控体系的拉伸目标", "summary": "从零搭建监控体系", "signals": ["achievement", "autonomy"]},
    {"source": "文档", "observation": "写了一篇 5000 字的架构复盘，把踩过的坑讲透", "signals": ["achievement", "competence"]},
    {"source": "Agent 交流", "observation": "和 AI 反复追问性能优化的更优解，不满足于第一个答案", "signals": ["achievement", "competence"]},
    {"source": "周会", "observation": "主动牵头跨团队的稳定性专项，协调三个组", "signals": ["power"]},
    {"source": "协作", "observation": "较少参与团队活动，多为独立作战", "signals": ["relatedness_low"]}
  ]
}
```

字段说明：

- `context.role` / `tenure`：岗位与任期（不含身份标识）。
- `context.audience`：`self` 或 `manager`，决定建议视角。
- `context.scenario`：可选的脱敏工作场景，帮助把下一步写得贴近现实；缺失时不得编造，需从证据归纳或标记待补。
- `context.action_scenes`：可选的维度到短场景名映射，用于让“具体下一步”使用短、真实、可回溯的场景标题；每个场景必须能回指 `evidence[]`，不能自行发明。
- `context.output`：可选的交付偏好。`detail=full` 表示完整总分式文字报告；`feishu_doc=true` 表示生成飞书云文档；`geometry_board=true` 表示生成并关联 Geometry Blue 画板。它们只指导 Agent 交付，不改变证据判断。
- `evidence[]`：每条一个观察，来自某个飞书资产。
  - `source`：资产类型（OKR / 文档 / 周会 / Agent 交流 / 协作 / 消息）。Agent 交流指员工与 codex/claude/豆包企业版等 AI 的会话。
  - `observation`：具体行为描述（脱敏）。
  - `summary`：可选的短行为锚点，建议 8–16 个汉字，供结论表使用；完整证据仍保留在 `observation`。
  - `signals`：这条证据指向的维度。取值：
    - 麦氏：`achievement` / `affiliation` / `power`
    - SDT：`autonomy` / `competence` / `relatedness`
    - SDT 低满足信号：`autonomy_low` / `competence_low` / `relatedness_low`

## 团队诊断输入

```json
{
  "team": "稳定性小组",
  "members": [
    {"alias": "成员A", "primary": "achievement", "secondary": "power"},
    {"alias": "成员B", "primary": "affiliation"},
    {"alias": "成员C", "primary": "achievement"}
  ]
}
```

`alias` 用脱敏代号，不用真名。`primary`/`secondary` 取麦氏三需要的 key。

## 禁止字段

输入不应包含姓名、工号、邮箱、手机号等身份标识，也不应包含薪酬历史、健康、家庭、年龄、性别、民族、宗教等敏感信息。脚本检测到会拒绝运行。`role`、`tenure` 这类岗位上下文不受影响。
