# AGDS Preview · DeepSeek Harness

**公开试用 · 0.1.0-preview.4-dsh.1 · bzx**

这个版本包含 18 个 AGDS 技能，覆盖项目初始化、编排、设计、制作、工程、美术、音频、质量验证、项目记忆、独立评审和能力改进。角色职责说明随包提供。Harness 原生角色注册和用量统计尚未接入。

## 安装

1. 将 ZIP 解压到你选定的目录。在 DeepSeek Harness 左侧打开 **插件 → 添加插件**，选择解压后的 `plugin` 文件夹，它包含 `package.json`。
2. 如果已装过旧版 AGDS Preview 本地插件，先停用并移除旧条目，再添加这个目录。旧版项目级包通过 `.dsh/skills` 加载，试用新版时请从新版解压目录开启会话。
3. 启用插件并新建会话。请保留解压后的目录，Harness 会从该目录读取技能。

## 首岛 Unity 示例

将本 README 所在目录选为 Harness 工作目录，再通过 Unity Hub 打开 `examples/FishingShelter/UnityProject`。先按[首岛练习说明](examples/FishingShelter/README.md)运行自动验收，再尝试给 Harness 一个只读任务：

> 请检查首岛渔具棚预制体的起始场景和验收结果。先选用合适的 AGDS 技能，说明哪些结果已有证据、哪些需要进一步验证。保持项目文件不变。

试用面向 DeepSeek Harness 0.2.2-rc.1。真实模型会话使用你已有的 DeepSeek 登录或连接。Unity 检查也可独立运行。

## 反馈

请到 [Issues](https://github.com/baizixn/agds-preview/issues) 提交 Harness 版本、操作步骤和实际结果。试用范围见[公开试用条款](LICENSE.md)。
