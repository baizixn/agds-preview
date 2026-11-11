# 实现前的引擎能力检查

用于新引擎能力、准备手写引擎/组件可能已提供的基础机制，或能力不确定会明显影响方案的任务。在原任务里完成，不另建研究项目。熟悉且已有当前版本证据的局部修复直接复用原决定，不新增网页、代理、研究报告或 Owner 门槛。

## 实际执行顺序

1. **读取现场版本。** `inspect` 从明确指定的 Unity 工程根读取 `ProjectSettings/ProjectVersion.txt`、`Packages/manifest.json`、`Packages/packages-lock.json`，保存内容指纹与声明/解析版本。它不启动编辑器，也不证明实际运行编辑器或已成功导入组件。仓库根不一定是引擎根，不能靠名称猜目录。
2. **查看已有实现。** 按需求追到当前入口、使用点、已安装组件和相关源文件；把实际读过的文件或有边界的检索输出作为证据。检索不到只说明本次检索范围没发现，不能证明整个引擎不支持。
3. **核对现成能力。** 对新机制查对应版本的官方 API、组件说明、限制和必要的变更记录。用 `capture` 保存实际取得的官方版本页及元数据；已经保存且完整的同版本资料可离线复用，不在每次检查时联网。在线来源优先一手资料，本地已安装源码可补充，不用无版本教程代替当前适用性。
4. **作出有依据的选择。** 选择复用项目实现、原生接口、原生加业务胶水或自研。记录候选、限制、需求缺口和证据；原生存在不等于适合目标线程、生命周期、平台、性能或许可条件。选择自研要有具体缺口；`unknown` 不能直接变成“不支持”。需要实测才能判断的事实保留为待探针，不拿文档当运行结果。
5. **执行检查。** `check` 检查版本、引用、哈希、选择字段与必要探针是否齐全；缺证、错版或失效返回非零及明确原因，相关功能实现等待补证。已授权的只读调查、最小探针和无关工作可以继续。它只检查机械一致性，工程负责人仍对资料解读和方案适配负责。
6. **按原授权实施。** 命令式实现可走 `guard`，它重新检查后才启动给定命令，缺证或只有调研权限时不启动。直接使用编辑工具时，先把 `check` 结果留在原任务中，交源评审时一并提供；缺少该结果就不能声称已完成实现前能力检查。该工具不会授予新权限，也不全局拦截终端、编辑器或 `apply_patch`。

不要为了通过检查升级引擎、安装新组件、扩大自研范围或编造探针。已有任务的授权、暂停、允许路径、独立设计/源评审仍有效。

## 工具

脚本为当前技能目录下的 `scripts/engine_capability_check.py`，Python 3.11+、标准库。实际输入与输出放在游戏项目原任务的技术记录目录，或独立测试目录，不放共享 Studio 源码。以下路径是示意：

```text
python -X utf8 <script> inspect --root <明确的Unity工程根> --output <任务目录>/engine-inventory.json
python -X utf8 <script> capture --url <带版本的官方URL> --directory <任务目录>/sources
python -X utf8 <script> check --record <任务目录>/engine-choice.json --output <任务目录>/engine-check.json
python -X utf8 <script> guard --record <任务目录>/engine-choice.json -- <已获授权的命令及独立参数>
```

`capture` 首版接受 Unity 官方文档域及其安全重定向，保存原文、可读文本与来源元数据，限制下载大小及超时；缓存验证失败不假装命中。版本页变化需要显式刷新，项目版本或相关源文件变化则重新核对决定。保留旧记录，不回写历史使它“当时已经通过”。

其他引擎首版自动盘点返回未适配，不从目录名推断版本。工程负责人应改用该引擎可核实的版本来源和官方能力调查，并明确自动门控未覆盖；重要未知仍需补证或有依据的方案决定，不能借未适配跳过调查。不要宣称此工具已经验证其他引擎。

## 决定记录

`engine-choice.json` 不是“已检查=true”表单。它必须绑定实际盘点与原任务文件、实际项目检索和官方来源；引用内容变化后原记录失效。结构如下，具体字段以工具错误信息为准：

- `schema_version: 1`；`inventory` 为 `inspect` 输出文件。
- `task` 包含稳定 `id`、原任务 `source: {path, sha256}`、`trigger`（`new_capability`、`replacement`、`uncertainty`、`routine_fix`）及已有任务的 `permission`（`inspect`、`probe`、`implementation`）。权限字段只抄录原授权，不能自授。
- `existing` 包含 `status`（`found`、`none`、`unknown`）、`summary` 和证据 ID 数组 `evidence`。发现或未发现均应有实际、限定范围的本地检查。
- `native` 包含 `candidate`、`status`（`fits`、`partial`、`unsuitable`、`unknown`、`not_needed`）、`reason` 和 `evidence`。新机制的前三种判断需当前版本一手依据；`not_needed` 只适用于有当前证据的现有实现复用。
- `decision` 包含 `path`（`existing`、`native`、`native_with_glue`、`custom`、`unresolved`）、`reason`、`gaps`。部分适用与自研都必须具体列缺口；不把没有调查结果写成不支持。
- `probe` 包含 `required`、`result`（`not_required`、`not_run`、`pass`、`fail`、`inconclusive`）和 `evidence`。必要探针必须有当前上下文的真实结果；由负责者判断是否需要探针，工具不靠关键词猜风险。
- `evidence` 列表的每项有唯一 `id`、`kind`（`local`、`official`、`probe`）、`path`、`sha256`。`official.path` 指向 `capture` 元数据，工具会继续核对原文和可读文本哈希、官方来源及版本范围。`probe` 项还要有 `context: {environment_fingerprint, task_sha256}`，绑定当前盘点及任务来源；日志内容没变，不代表它仍适用于新版本或新任务。源码、任务和探针日志是实际文件引用；空引用、缺失文件或改变后的引用不能通过。

相对路径按记录文件所在目录解释；由 `capture` 生成的缓存路径按其元数据解释。提供真实来源比填满字段更重要。工具不能离线证明自然语言结论真实或日志由谁产生，源评审要看原资料、适配理由和必要探针，不能只看退出码。

日常交付只加一句实现选择与证据位置即可。检查通过不是编译、运行、设备、性能或 Owner 验收；这些层次继续分别报告。
