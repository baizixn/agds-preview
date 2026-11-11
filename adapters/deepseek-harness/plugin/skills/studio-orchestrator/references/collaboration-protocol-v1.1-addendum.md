# AI Game Development Studio 协作协议 V1.1 增补内容

- 状态：原 V1.1 基线与本次迭代条款分开追踪；各版本的采用和部署以对应记录为准
- 适用范围：AI Game Development Studio 的 Agent、Skill、Reviewer、上下文、审批与项目记忆治理

## 11. Agent 标准定义规范

每个 Agent 必须由以下四部分组成：

Agent = Role Definition + Skills + Memory + Permission

### Role Definition

定义 Agent 的身份、目标和职责边界。

必须包含：

- Agent ID
- Agent Name
- Mission
- Responsibilities
- Collaboration Scope
- Forbidden Actions

### Skills

Skill 是 Agent 可调用的专业能力模块，不等同于角色本身。

每个 Skill 必须定义：

- Skill ID
- 所属 Agent
- 输入要求
- 输出格式
- 验收标准
- 适用场景

例如：

Game Design Agent 可以拥有：

- Gameplay Loop Design Skill
- Competitor Analysis Skill
- System Design Skill

Engineering Agent 可以拥有：

- UE5 Architecture Skill
- VR Interaction Skill
- Performance Optimization Skill

---

## 12. Reviewer Agent 评审机制

除 Specialist Agent 外，系统增加 Reviewer Agent。

Reviewer Agent 不负责生产内容，而负责独立评价结果。

职责：

- 检查逻辑完整性
- 发现风险
- 提供反向意见
- 验证是否满足任务目标

规则：

1. Reviewer 不应预先获得作者期望结论。
2. Reviewer 输出只能作为 Candidate 评审依据。
3. Reviewer 无权直接修改正式项目事实。

---

## 13. Context Routing 上下文路由规范

Agent 不允许默认读取全部项目资料。

所有任务必须经过 Context Routing。

读取顺序：

1. PROJECT_STATE
2. CONTEXT_MAP
3. 当前任务信息
4. 关联 Decision
5. 必要领域文档

禁止：

- 默认读取全部历史记录
- 使用未关联项目资料
- 使用未经批准的 Candidate 作为事实

不同 Agent 应拥有不同上下文范围：

Game Design Agent：

读取：

- Game Documents
- Research
- Player Feedback

Engineering Agent：

读取：

- Technical Documents
- Approved Design
- Performance Data

Art Agent：

读取：

- Art Direction
- Asset Requirements
- Approved Concepts

QA Agent：

读取：

- Build Information
- Test Requirements
- Previous Issues

---

## 14. Approval Gate 审批节点

以下事项必须经过 Project Owner 审批：

- 核心玩法变化
- 产品定位变化
- 美术风格基线变化
- 平台和商业策略变化
- 大规模技术架构调整
- Agent 或 Skill 基线升级

以下事项可在授权范围内自动执行：

- 为当前目标发现问题、实现局部可逆修复、运行相关检查并继续迭代
- 文档整理
- 格式检查
- 信息索引维护
- 可逆测试
- 局部优化建议

早期开发按 [Owner interaction](../SKILL.md#owner-interaction) 区分普通修复、重要改动和方向/发布决定。普通修复不逐项等待 Owner，也不默认增加 QA/Reviewer 链；重要改动在完整交付点做独立评审。已有明确授权覆盖的动作不重复申请。Candidate 未正式采用，不妨碍已授权的实施与试验；检查通过也不自动成为 Owner 采用决定。其他项目已有的明确限制不会因本规则自动解除。

---

## 15. Project Memory 数据模型

Project Memory 不保存所有过程，而保存项目有效状态。

核心数据：

### Project State

当前项目阶段和目标。

### Task State

任务、负责人、状态、输出。

### Decision State

已确认设计决策及影响范围。

### Agent State

Agent 当前任务、能力状态和最近结果。

### Feedback State

用户纠正、失败案例、能力改进建议。

---

## 16. Agent 能力升级机制

Agent 不允许根据单次任务结果自动修改自身能力。

能力升级必须经过：

1. 收集失败案例或用户反馈。
2. 判断是否属于通用能力问题。
3. 修改 Skill 候选版本。
4. 执行验证。
5. Project Owner 审批后升级。

---

## 17. AI Game Studio 当前运行模式

当前早期迭代阶段以更快发现、修复和验证问题为目标。AI 在已授权任务范围内负责分析、实施、相关检查与简短结果记录，并按需要组织专业协作；不把执行和测试仅列为未来能力。

Project Owner 在方向、重要范围、费用、质量标准及正式共享版本/发布等需要新决定时介入。普通修复完成后可继续同一目标，无需逐次采用。

两轮指针对同一阻塞、基于明确原因作出的纠正，不是修改文件数、提交数或整个任务的修改总数。两轮仍未解决，或没有新的有效证据时，先暂停当前失败思路，核对原假设、实际结果及两轮失败，复查必要源码或可靠资料并调整方法；必要时请求有界独立意见，不增加每次必走的评审链。有新证据支持的下一步可在已有授权内有限推进；换任务名、改错误描述或微调同一失败方案不能重置限制。仍缺可行方法，或需要改变范围、架构取舍、费用、权限或质量目标时，才提出那个具体 Owner 决定。无关的已授权修复可继续，失败和限制须保留，不以凑齐通过掩盖停滞。
