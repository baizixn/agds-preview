# 阶段进度：聊天卡与按需面板

日常默认直接在聊天交付里显示简短状态，不单独生成网页，不为进度展示调用额外代理。制作人维护范围、覆盖和更新时点；实现与验证结论引用各自负责人的证据，Owner 验收单列。它是原阶段台账的视图，不是新的质量门，也不能替代可运行交付。

示例（虚构数字，不是任何真实项目状态）：

```text
当前阶段：完整单局流程 · 进行中
已实现 ██░░ 2/4 ｜已验证 █░░░ 1/4
Owner 验收：尚未进行
本次交付：局部测试，仅测试进入与游玩
尚未完成：结算、重新开始
```

未知则写“未核实”，不画假的比例。沿用项目现有计划与执行记录即可，不为每条回复建立新文件或重算历史。收到实际交付/测试结果时更新原记录；只看进度不创造新事实。

以下网页工具保留为可选项。只有用户明确请求打开或刷新阶段面板时，才核对数据并生成或启动网页；不要因普通交付、反馈或聊天结束自动运行它。

## 维护与查看

1. 读取项目当前权威阶段计划和最新任务/验证记录。沿用原阶段、条目 ID、Must/Should/Could/Deferred 与验收要求；不得为提高比例拆细已完成项、遗漏未完成项或私自缩小分母。
2. 打开网页时，将原台账导出为项目自己的 `AI_Records` 下的 `stage-progress.json`，或更新已有快照。已有结构化执行台账时从它生成，不双向维护第二份状态；只有计划尚无执行台账时，此 JSON 可保存以原计划条目 ID 为键的执行状态与证据。计划仍是范围权威，JSON 不改写或批准计划。
3. 更新本次交付的类型、摘要、测试范围、预期与未就绪部分。反馈先区分：原承诺未做、已做但有缺陷、测试/环境问题、范围新增；前两者回到原条目，后两者保留证据或变更来源。正常修复继续已授权工作，范围调整沿用原审批责任。
4. 执行 `validate`，再 `render` 或 `serve`。阶段计划/台账、执行状态、证据、可玩交付分别保留。未知写 `unknown`，未运行写 `not_run`；不可用继承项目的验证、文档完整或编译通过代替本阶段验收。
5. 在范围变化、实质交付、收到测试结果时更新原执行记录并给聊天卡；不要求同步生成 HTML。跨任务交接保留现有记录路径、原计划来源、最后更新时间、未完成项和下一验证。已保留的网页展示旧快照，用户要求打开时再核对刷新，避免让 Owner 把一次修复完成理解成阶段完成。

从技能目录定位脚本，Python 3.11+，无第三方依赖：

```text
python -X utf8 <技能目录>/scripts/stage_panel.py validate --input <项目内JSON>
python -X utf8 <技能目录>/scripts/stage_panel.py render --input <项目内JSON> --output <项目附属目录>/index.html
python -X utf8 <技能目录>/scripts/stage_panel.py serve --input <项目内JSON> --port 0
```

静态页可离线打开；它标明更新时间，需要 AI 更新数据并重新生成。`serve` 只监听本机，启动后读取实际返回的私有 `url`，通过可用浏览器面板打开；无该工具时给同一地址。服务读取变化后更新展示，不扫描聊天、自动判断实现或改写数据。关闭服务不删除记录。不要公开托管项目进度。

## 输入与口径

输入为 JSON，`schema_version: 1`，包含项目名 `project`、记录时间 `updated_at`、`source`、`delivery` 与 `stages`。

- `source`: 原台账/计划的绝对 `path`、内容 `sha256` 和展示 `label`。来源缺失或摘要不一致时拒绝显示新的进度，先回查范围并重新导出；不能只刷新摘要来绕过范围核对。
- `delivery`: `kind` 为 `progress`、`partial_test` 或 `stage_review`，并提供 `summary` 文本与 `test_scope`、`expected`、`not_ready` 文本数组。`stage_ids` 标明本次交付关联阶段；局部测试必须指定阶段与非空测试范围，不能把全局交付自动套到当前选中阶段。局部可测可以早于阶段完成；必须明确只测哪些行为。
- 每个阶段包含 `id`、`title`、`goal`、`dependencies`、`scope_state`（`candidate` 或 `approved`）、`scope_evidence`、`execution`（`planned`、`active`、`paused`）、`artifact_revision`、`owner_acceptance`、`exit`、`conditions`、`tests`、`items`。前置条件是原计划要求，不自动等于已确认现场故障。
- `owner_acceptance` 含 `state`（`pending`、`accepted`、`rejected`）与 `evidence`。批准范围和接受交付不是同一决定。候选范围不能显示阶段就绪；验收接受需要明确来源和满足本工具所展示的就绪条件。若实际采用有豁免，先反映已批准范围/验收合同调整，保留原记录，不能强行把未通过项改成 Pass。
- 每项包含 `id`、`title`、`scope`（`Must`、`Should`、`Could`、`Deferred`）、`source_ref`，以及 `implementation` 和 `verification`。ID 稳定，不因标题改写换号；延期项保留在页面上。
- `implementation`: `state` 为 `unknown`、`todo`、`in_progress`、`done`、`blocked`，附 `evidence` 和 `revision`。`done` 需有来源且版本匹配阶段 `artifact_revision` 才计已实现；代码存在不是自动完成证据。
- `verification`: `state` 为 `unknown`、`not_run`、`pass`、`fail`、`stale`、`inconclusive`，附 `evidence`、`revision`、`environment`。通过需引用与当前交付版本匹配的验证记录及环境；一次局部检查只证明对应条目，不自动证明整项体验。修改影响旧证据时回到待复测。

进度分母只含当前范围的 Must 项，展示项数覆盖而非工时、质量评分或剩余时间。未核实部分醒目标出；全未知或零分母不显示虚假的完成百分比。Should/Could/Deferred 继续可见。只有已批准且非空的全部 Must 有当前实现与通过证据，才提示“待 Owner 验收”；工具不授权执行、不判断证据真实性，也不自动接受成果。

已有文档中的 25/50/80/100% **预算检查点**与本页覆盖率无关，不可混用。
