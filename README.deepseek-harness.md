# AGDS Preview · DeepSeek Harness

**邀请制候选 · 0.1.0-preview.2-dsh.1 · bzx**

这份 Preview 供 DeepSeek Harness 试用。它包含项目初始化、工程、质量验证、项目记录和评审五个技能，以及原有的首岛渔具棚 Unity 练习。场景、Blender 源文件和 Unity 检查脚本与 Codex 版使用同一份源内容。

## 从解压目录开始

1. 把 ZIP 解压到短路径，例如 `C:/Unity/AGDSDeepSeek`。确认同一目录下能看到 `.dsh`、`examples` 和本 README。使用独立目录，避免把它解压到另一个 Git 仓库内部。
2. 在 **DeepSeek Harness** 中把包含本 README 的目录选为工作目录。Harness 从这里的 `.dsh/skills` 发现 AGDS 技能。打开 Unity 时，再把 `examples/FishingShelter/UnityProject` 加到 Unity Hub。
3. 先按[首岛练习说明](examples/FishingShelter/README.md)完成 Unity 入门检查。在 Harness 里打开一个只读会话，让它载入工程和 QA 技能，读起始场景和验收结果，再说明建议改动。

> 请载入 engineer-game 和 assure-game-quality，按首岛 README 做只读检查。确认工程路径、起始场景、自动验收结果和允许修改的范围。先报告计划，等我确认后再改。

如果习惯用终端，在本 README 所在目录运行以下命令。将 `<Harness 安装目录>` 替换为本机安装目录。若 `dsh` 已在 PATH 中，可直接运行 `dsh headless`。

```powershell
$dsh = '<Harness 安装目录>/resources/runtime/cli/bin/dsh.cmd'
& $dsh headless --permission-mode read-only --approval-policy never '请载入 engineer-game 和 assure-game-quality，按首岛 README 做只读检查。'
```

本版面向 DeepSeek Harness **0.2.2-rc.1** 的项目级技能入口。真实模型会话使用你自己已配置的 DeepSeek 登录或模型连接。首岛 Unity 检查可单独运行。

## 反馈

请把 Harness 版本、操作步骤、预期和实际结果发给邀请人。试用边界见[邀请试用条款草案](PREVIEW-TERMS-DRAFT.md)。
