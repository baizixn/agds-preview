# AGDS Preview

**邀请制候选 · 0.1.0-preview.2 · bzx**

AGDS 是一套在 Codex 中使用的游戏开发技能。这个候选包含项目初始化、工程、质量验证、项目记录和评审技能。首个练习让你检查一个独立目录，并预览 AGDS 会为它建立哪些协作文件。

## 安装前

当前候选供 bzx 本地审阅。试用条款确认并收到邀请后，再按下面步骤安装。请准备 Windows PowerShell、已登录且支持 `codex plugin` 的 Codex CLI，以及 Python 3.11 或更新版本。解压时保留隐藏目录。当前命令已核对 CLI 入口，完整安装仍待在干净环境验证。

在含有本 README、`.codex-plugin` 和 `skills` 的目录打开 PowerShell：

```powershell
codex --version
python --version
codex plugin marketplace add . --json
codex plugin add agds-preview@agds-bzx-preview --json
codex plugin list --marketplace agds-bzx-preview --json
```

列表中应出现 `agds-preview`，版本为 `0.1.0-preview.2`，安装和启用状态均为真。若命令不受支持、来源冲突或版本不一致，请保存错误和 CLI 版本，发给 bzx 核对。

## 第一次试用 · 首岛渔具棚预制体

打开 [原创首岛示例](examples/FishingShelter/README.md)。先在 Unity 对起始场景运行检查，再把场景、检查结果和交付要求交给 AGDS。练习和自动验收只覆盖三个棚位。码头、沙岸、步道和植被是两版共用的布景。只需 Unity 就能完成入门检查；修改棚子的 Blender 源资产时再打开 Blender。

## 反馈与移除

反馈请发给邀请人，并附 Preview 版本、Codex CLI 版本、复现步骤和实际结果。只提供与问题有关且可分享的日志。

```powershell
codex plugin remove agds-preview@agds-bzx-preview
codex plugin marketplace remove agds-bzx-preview
```

预期使用范围见 [邀请试用条款草案](PREVIEW-TERMS-DRAFT.md)。
