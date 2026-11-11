
# DeepSeek Harness 适配

本分支从同一份 Preview 源码生成 Harness 项目包。打包时将 5 项技能和相邻参考放到 `.dsh/skills/`，同时带上共用的首岛示例与邀请试用条款。

在仓库根目录用 Python 3.11 或更新版本运行。生成器读取当前提交中跟踪的文件，输出路径由你指定。

```powershell
python -B adapters/deepseek-harness/package_preview.py --output ./AGDS-Preview-DeepSeekHarness-0.1.0-preview.2-dsh.1.zip
```

解压并按 [Harness 使用指南](../../README.deepseek-harness.md) 打开项目。该方式面向项目级技能加载。

## 验证范围

- 本机使用 DeepSeek Harness `0.2.2-rc.1`。回环测试确认 5 个技能可发现，并用原生工具实际读取工程和质量验收技能。
- 一次真实 `deepseek-flash` 只读会话自行选择了质量验收和候选评审技能。它区分了起始场景自检通过、起始场景交付失败，以及参考版的棚区验收通过。工程改造任务的自主选技仍待验证。
- Unity 示例由两种宿主共用。Blender 源文件已清理本机路径元数据并重新打开检查，网格、UV 和打包色板签名一致，重新导出为 408 / 132 三角面。
