# 上游与先例

## 上游来源

- 上游项目：[manager-dot-dev/manager-skills](https://github.com/manager-dot-dev/manager-skills)
- 主要参考 Skill：
  - [skills/engineer-motivation](https://github.com/manager-dot-dev/manager-skills/tree/c47ebc7adc3ef84056f059e2a426077cfe12de8c/skills/engineer-motivation)（三驱动力框架）
  - [skills/career-development](https://github.com/manager-dot-dev/manager-skills/tree/c47ebc7adc3ef84056f059e2a426077cfe12de8c/skills/career-development)（发展阶段视角）
- 固定版本：`c47ebc7adc3ef84056f059e2a426077cfe12de8c`
- 上游许可证：MIT
- 核验时间：2026-08-17（Asia/Shanghai）

## 保留与扩展

上游 `engineer-motivation` 提供了一个面向工程管理者的三驱动力（成长/连接/影响）直觉框架。本包保留其「按驱动对齐授权」的核心洞察，并做了实质性重构与升级：

- **升级为双学术模型**：用麦克利兰成就动机理论（成就/亲和/权力）替代上游的直觉三分类，并叠加自我决定理论 SDT（自主/胜任/归属）判断动机状态。方向 × 状态，带科学诊断依据，而非拍脑袋分类。
- **飞书数据资产驱动**：从员工在飞书沉淀的 OKR、文档、周会表现，以及员工与 AI Agent（codex / claude / 豆包企业版等）的交流内容里只读取行为证据做诊断，而非单一问卷。
- **证据链输出**：每条结论回溯到具体资产的具体行为，带推断逻辑和置信度，并声明「行为推断，与本人认知可能有差」。
- **双视角**：员工自测（发展建议）与 Leader/HR 他评（管理建议）切换。
- **场景泛化**：从工程师泛化为任意岗位员工。
- **首次使用科普**：用大白话解释六个维度，降低学术门槛。
- **隐私硬约束**：消息仅辅助且他评透明、只对直属成员、不做标签/打分/排序/背对背画像；脚本拒绝含身份或敏感字段的输入。
- **假数据回放与单元测试**：8 项测试覆盖主驱动识别、证据链、双视角差异、双模型分区、SDT 低满足、团队缺位、隐私拒绝。

## 学术模型出处

- **麦克利兰成就动机理论**：David C. McClelland, *The Achieving Society* (1961) 及 Acquired Needs Theory，提出成就（nAch）、亲和（nAff）、权力（nPow）三种内在需要。
- **自我决定理论（SDT）**：Edward L. Deci & Richard M. Ryan, Self-Determination Theory，提出自主（Autonomy）、胜任（Competence）、归属（Relatedness）三个基本心理需求，是当代职场动机研究最主流的框架之一。

模型为中文语境重述与工程化落地，非上游文本或任何专有测评问卷的逐字复制；商用前请自行确认相关框架的授权要求。
