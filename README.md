# AGDS Preview

**邀请制候选 · 0.1.0-preview.3 · bzx**

本候选包含 18 个技能，与 DeepSeek Harness 邀请版的清单一致。它们覆盖项目初始化、编排、设计、制作、工程、美术、音频、质量验证、项目记忆、独立评审和能力改进。角色说明随包提供，供分配任务时参考。

## 安装前

当前候选供 bzx 本地审阅。试用条款确认并收到邀请后，再按下面步骤安装。请准备 Windows PowerShell、已登录且支持 `codex plugin` 的 Codex CLI，以及 Python 3.11 或更新版本。解压时保留隐藏目录。请从本目录安装，并在新会话里使用插件。

在含有本 README、`.codex-plugin` 和 `skills` 的目录打开 PowerShell：

```powershell
codex --version
python --version
codex plugin marketplace add . --json
codex plugin add agds-preview@agds-bzx-preview --json
codex plugin list --marketplace agds-bzx-preview --json
```

列表中应出现 `agds-preview`，版本为 `0.1.0-preview.3`，安装和启用状态均为真。如果之前装过旧版，请先按下文移除旧插件和旧来源，再从新版目录重新安装。若版本仍不一致，请把 Codex 版本和实际显示的插件版本发给 bzx。

## 第一次试用 · 首岛渔具棚预制体

打开 [原创首岛示例](examples/FishingShelter/README.md)。先在 Unity 对起始场景运行检查，再把场景、检查结果和交付要求交给 AGDS。练习和自动验收只覆盖三个棚位。码头、沙岸、步道和植被是两版共用的布景。只需 Unity 就能完成入门检查；修改棚子的 Blender 源资产时再打开 Blender。

## 反馈与移除

反馈请发给邀请人，并附 Preview 版本、Codex CLI 版本、复现步骤和实际结果。只提供与问题有关且可分享的日志。

```powershell
codex plugin remove agds-preview@agds-bzx-preview
codex plugin marketplace remove agds-bzx-preview
```

预期使用范围见 [邀请试用条款草案](PREVIEW-TERMS-DRAFT.md)。
