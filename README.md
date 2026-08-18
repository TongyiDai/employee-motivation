> “Satisfying human needs for competence, relatedness, and autonomy creates sustainable motivation.” — [Edward L. Deci, Richard M. Ryan et al.](https://selfdeterminationtheory.org/SDT/documents/2009_StoneDeciRyan_JGM.pdf)

<h1 align="center">员工动机诊断</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Agent%20Skill-agentskills.io-2F6BFF" alt="Agent Skill">
  <img src="https://img.shields.io/badge/license-MIT-3fb950" alt="License MIT">
  <img src="https://img.shields.io/badge/model-McClelland%20%C3%97%20SDT-2F6BFF" alt="Dual model">
  <img src="https://img.shields.io/badge/python-%3E%3D3.8-3572A5" alt="Python >=3.8">
  <img src="https://img.shields.io/badge/works%20with-Codex%20|%20Claude%20|%20Cursor%20|%20TRAE-555" alt="Works with major agents">
</p>

基于员工在飞书上沉淀的真实工作资产（OKR、文档、周会表现，以及员工与 AI Agent 的交流内容），诊断「他被什么驱动、动机状态如何」，并按使用者视角给出对应建议。Skill 用两个成熟动机模型做骨架，多维度、带证据链地推断。完整模式采用“短总览、长详情、场景行动”：结论表负责快速判断，详情负责讲透证据，下一步落到真实项目、会议或流程。

## 特色：双模型骨架，带科学诊断依据

<p align="center">
  <img src="assets/boards/1-dual-model.png?v=20260817" alt="双模型：麦克利兰三需要定方向 × SDT 定状态" width="90%">
</p>

市面上多数「动机测试」是自造的分类，缺乏理论根基。这枚 Skill 的核心区别是**叠加两个经过验证的动机模型**：

- **麦克利兰成就动机理论**（方向）——判断被什么内在需要驱动：
  - **成就 nAch**：想把事做到最好、爱挑战难题，满足感来自「搞定一件难事」本身。
  - **亲和 nAff**：想要好的关系和归属感，重视团队、协作、和同事的连接。
  - **权力/影响 nPow**：想影响他人、推动结果、有话语权（组织权力是好领导的底色）。
- **自我决定理论 SDT**（状态）——判断动机质量与是否被满足：
  - **自主 Autonomy**：能自己决定、认同做事的理由，而非被逼。
  - **胜任 Competence**：有「我有能力、在变强」的体验。
  - **归属 Relatedness**：和人有连接、被在意、属于团队。

**方向 × 状态 = 立体诊断**：麦氏告诉你「他朝哪使劲」，SDT 告诉你「这股劲顺不顺、被不被满足」，而不是贴一个标签就完事。首次使用时，Skill 会用大白话解释这六个维度，非专业用户也能秒懂。

## 基于飞书资产，每条结论都有支撑逻辑

<p align="center">
  <img src="assets/boards/2-evidence-chain.png?v=20260817" alt="飞书资产→双模型→带证据链的诊断输出" width="90%">
</p>

诊断以飞书工作资产为主要依据（OKR、文档、周会，以及**员工与 AI Agent 的交流内容**——一个人和 codex/claude/豆包企业版等 AI 怎么对话，很能反映他关心什么、怎么工作，是 agent-agnostic 的特色信号源）。

输出先给一张**短结论表**，把「被什么驱动 → 现在的状态 → 这意味着什么 → 所以该怎么办」串成一条逻辑线，让驱动方向和满足状态的关系一目了然。表内只保留一句话判断和来源/行为短锚点，完整观察放到后面的详情：

| 诊断维度 | 诊断结果 | 支撑论据 |
| --- | --- | --- |
| 你被什么驱动 | 主导是成就需要，其次是权力/影响需要，亲和需要偏弱。 | 1. 成就需要（强）：本季度给自己定了从零搭建监控体系的拉伸目标；写了一篇 5000 字架构复盘，把踩过的坑讲透<br>2. 权力/影响需要（中）：主动牵头跨团队稳定性专项，协调三个组 |
| 你现在的状态 | 归属 偏低；自主、胜任 尚可。 | 1. 归属（偏低）：较少参与团队活动，多为独立作战<br>2. 自主（尚可）：本季度给自己定了从零搭建监控体系的拉伸目标<br>3. 胜任（尚可）：写了一篇 5000 字架构复盘，把踩过的坑讲透 |
| 这意味着什么 | 你想要的是「成就需要」那类的事，但当前「归属」偏低——方向对，动力却在流失，这是最该优先补的地方。 | 1. 从「搞定一件难事」本身获得满足，不是靠钱或头衔<br>2. 和团队连接偏弱、有点孤军奋战，时间长了动力会被磨掉 |
| 所以该怎么办 | 把机会给对，同时补上偏低的需求。 | 1. 争取有难度、能拉伸能力的项目；把「做到最好」的标准显性化，让成果可被看见<br>2. 补团队连接、别让你长期孤军奋战 |

诊断结果是大白话总结，支撑论据用编号分条、均来自飞书资产或与 Agent 的交流。结论表之后，再给每个维度的完整证据链（倾向 → 支撑证据 → 推断逻辑 → 置信度 → 替代解释/需确认）。行为不完全等于动机，结论是**推断**，最终需本人确认。

## 文档风格：专业判断 + 人在场

完整报告默认采用“同事风格 + 咨询风格”：标题写判断，段落写证据，行动写责任和时间。每个详情小节按“判断 → 证据 → 推断 → 这意味着什么”展开；语气专业、克制、有温度，允许明确写出“我判断”“我倾向于”和“这里还不能确认”。

## 具体下一步：从判断回到真实工作

完整诊断不会停在“提升影响力、加强沟通”这类抽象建议。每条行动都绑定一个真实场景，并写清：具体动作、结果指标、时间锚点、决策/协作边界和复盘触发条件。证据不足时标记“待补场景”，不编造项目、指标或期限。

## 飞书云文档 + Geometry Blue 画板

用户要求报告或沉淀结果时，Skill 可同时交付当前对话中的完整文字总结和一份飞书云文档。文档保存完整证据链、场景化解释和具体行动，并默认关联 4 张 Geometry Blue 画板：总览画板紧跟文档标题，成为正文中的第一个块；中段 2–3 张分别解释驱动、状态、场景或行动。多张画板按主题分散插入，至少使用 3 种构图家族，并写入画板直达链接。

画板默认采用蓝色—米色—深蓝参考版式：`#375dfe` 主蓝、`#fdf0e0` 米色底、`#1a2240` 深蓝文字与边框、白色信息块。总览采用左右分栏，驱动采用“维度｜行为证据｜判断”表格，状态与行动采用 3 张编号卡片；标题、重点块、边框、留白保持统一，卡片文字与边缘线保留呼吸区，正文承载完整证据。

`主导驱动 → 当前状态 → 真实工作场景 → 下一步动作`

画板通过飞书文档中的可编辑白板资源块写入，写入后回读文档结构和画板插入点，区分“已生成、已插入、已写入、已验证”。没有写入权限时保留文字报告和本地 SVG，并明确说明阻塞环节。

## 两种模式，两种视角

<p align="center">
  <img src="assets/boards/3-audience.png?v=20260817" alt="员工自测给员工视角建议，Leader/HR 他评给管理视角建议" width="90%">
</p>

- **员工自测（audience=self）**：站在员工视角——你的主导动机、当前哪个需求没被满足、未来该争取什么机会、补哪一块。
- **Leader/HR 他评（audience=manager）**：站在管理视角——该成员被什么驱动、该分什么活、怎么激励、团队缺哪种驱动、怎么补位。

他评有硬边界：**只对自己直属成员、且过程对本人透明可复核**。

## 边界：帮人更懂自己，不给人贴标签

<p align="center">
  <img src="assets/boards/4-boundary.png?v=20260817-2" alt="用于发展性对话与授权；拒绝标签、打分、排序、背对背画像" width="90%">
</p>

结论用于**发展性对话与授权安排**，明确拒绝：性格标签、绩效打分、人员排序、背对背画像。对话消息只作辅助且他评须透明。详见 [references/boundaries.md](references/boundaries.md)。

## 快速开始

```bash
# 员工自测视角
python3 scripts/diagnose.py --input tests/fixtures/case-achievement.json --audience self --format markdown

# Leader/HR 他评视角
python3 scripts/diagnose.py --input tests/fixtures/case-achievement.json --audience manager --format markdown

# 团队构成诊断
python3 scripts/diagnose.py --team tests/fixtures/team.json --format markdown
```

飞书证据的只读读取契约见 [references/feishu-evidence.md](references/feishu-evidence.md)；模型详解见 [references/motivation-model.md](references/motivation-model.md)；输入格式见 [references/input-schema.md](references/input-schema.md)。

## 目录结构

```text
SKILL.md                       技能主文件（双模型、飞书资产、视角、科普块）
AGENT-GUIDE.md                 跨 Agent 使用须知
references/
  motivation-model.json        双模型六维度的机器可读真源
  motivation-model.md          模型说明（含首次使用科普）
  feishu-evidence.md           飞书资产 → 六维度证据映射
  driver-actions.md            驱动对齐的行动建议
  report-and-delivery.md       总分式报告、具体行动、云文档与画板交付规范
  input-schema.md              脚本输入格式
  boundaries.md                隐私与边界
scripts/
  diagnose.py                  双模型诊断器（证据链 + 场景化行动 + 视角切换 + 团队）
  render_boards.py             Geometry Blue 画板渲染
tests/                         假数据与单元测试
assets/                        画板场景与渲染图
```

## 面向所有 Agent

本 Skill 不绑定任何单一平台。任何能读取 `SKILL.md`、处理用户材料、执行本地 Python 脚本的 Agent 都可使用。使用方式见 [AGENT-GUIDE.md](AGENT-GUIDE.md)。

## 测试

```bash
python3 tests/test_diagnose.py
```

## 许可证与出处

MIT，见 [LICENSE](LICENSE)。上游来源（`manager-dot-dev/manager-skills`）、学术模型出处（McClelland / Deci & Ryan）与扩展说明见 [UPSTREAM.md](UPSTREAM.md) 和 [NOTICE](NOTICE)。模型为中文语境重述与工程化落地，非任何专有测评问卷的逐字复制。
