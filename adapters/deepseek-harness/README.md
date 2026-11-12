# DeepSeek Harness 适配

当前候选包含 18 个技能、共用的首岛 Unity 示例和公开试用条款。技能通过 Harness 插件面板加载。

在仓库根目录用 Python 3.11 或更新版本执行。生成器从当前 Git 提交读取文件。

```powershell
python -B adapters/deepseek-harness/package_preview.py --output ./AGDS-Preview-DeepSeekHarness-0.1.0-preview.4-dsh.1.zip
```

解压后按[使用指南](../../README.deepseek-harness.md)安装。只试用技能时，也可直接在插件面板选择本目录下的 `plugin` 文件夹。

上一版真实模型测试使用项目级加载。新版插件验证单独记录 18 个技能的发现和读取结果。
