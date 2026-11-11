# 首岛 · 把渔具棚交付成可复用模块

你在一个小岛的三处泊位摆好了渔具棚。原场景看得出用途，但棚子是散件，缺少统一的源资产和远景模型，而且中间的入口被挡住了。任务是整理出能维护、复用和验收的工程资产，同时保留码头、沙岸、步道、棚区和固定机位。

本练习使用为 Preview 重新制作的原创岛屿、网格和贴图。素材、代码和场景数据独立于商业项目。

## 一、打开起始工程并做只读检查

1. 准备 Unity **6000.5.10f1**。第一次导入需要取得 Unity URP 17.5.0 依赖。Windows 上把整个 `FishingShelter` 文件夹复制到短路径，例如 `C:/Unity/IslandPreview`，以免 Unity 导入深层依赖时触及路径长度限制。
2. 在 Unity Hub 添加 `UnityProject`，打开 `Assets/FishingShelter/Scenes/Shelter_Starter.unity`。在 Game 视图看岛屿，码头连着棚区，中间入口有阻挡物。
3. 运行 Unity 菜单 **AGDS → Shelter Exercise → Check Active Scene**。Console 应报告 `looseCubes=10`、`prefabRoots=0`、`blockedDoorways=1`、`lodGroups=0`。
4. 运行 **Check Delivery**。起始版预期被拒绝，提示需要三个棚子根对象。这和改造后使用的是同一个验收入口。
5. 在安装 AGDS Preview 后，新开 Codex 聊天并选择这个练习副本。可以直接粘贴下面的话。

> 请用 AGDS Preview 的 engineer-game 和 assure-game-quality 查看这个首岛练习。先解释起始场景的检查结果，列出交付差距和拟修改的文件。保持岛屿、码头、步道、三个泊位位置和固定镜头。自动检查脚本属于验收基准。只有我确认后才改造棚区。

## 二、走完整的 Blender → Unity 交付

如需让 AGDS 执行改造，告诉它可以写入练习副本里的 `Blender/`、`UnityProject/Assets/FishingShelter/Models/`、`Materials/Shelter.mat`、`Prefabs/` 和你另存的练习场景。先把 `Shelter_Starter.unity` 另存一份再编辑，保留起始版。参考成果可以在 `Shelter_Reference.unity` 查看。

| 要求 | 验收 |
| --- | --- |
| 源文件能继续修改 | 在 Blender **5.1.2** 打开 `Blender/Shelter.blend`，查看 LOD0 / LOD1 集合里的棚架、木板和屋顶。改一个屋檐尺寸，重新导出，看三个泊位是否同时更新。 |
| 三处使用同一资产 | 棚区三个根对象都引用 `Prefabs/Shelter.prefab`，位置不漂移。 |
| 两档真实网格 | Unity LODGroup 对应两个独立 FBX。近景 ≤ 1,500 三角面，远景 ≤ 600 且低于近景。 |
| 材质一致 | 所有棚体网格用同一个 URP Lit 材质和同一张贴图，Unity 导入尺寸上限为 1,024。 |
| 碰撞和外观 | 棚体用三个 BoxCollider。验收射线能进门，后墙和侧墙有阻挡。固定镜头下入口朝向码头一侧，三个棚子轮廓可读。 |

已有的可编辑源文件可以用 Blender 打开并调整。保存源文件后，在练习副本中从 PowerShell 运行以下命令。将 `<blender.exe 的路径>` 换成安装位置，Unity 会重新导入两个 FBX。

```powershell
& '<blender.exe 的路径>' --background './Blender/Shelter.blend' --python-exit-code 9 --python './Blender/shelter_source.py'
```

打开改好的场景，运行 **AGDS → Shelter Exercise → Check Delivery**。参考场景应报告三个 Prefab 实例、408 / 132 三角面、每棚三个碰撞体和 1,024 的贴图导入上限。场景检查使用 Unity 物理射线验证通道与阻挡，画面复核由你完成。

[起始版画面](Preview/01-starter.png) · [改造后画面](Preview/02-reference.png)

### 无界面重跑

也可以从本文件所在目录，用 Unity 可执行文件执行已保存场景的检查。关闭这个练习的 Unity 窗口后运行，等待命令结束，再查看 `island-check.log` 中的 `AGDS_SHELTER_CHECK`。

```powershell
& '<Unity.exe 的路径>' -batchmode -quit -projectPath (Resolve-Path './UnityProject') -executeMethod ShelterCapture.VerifyShippedScenes -logFile (Join-Path (Get-Location) 'island-check.log')
```

## 原始素材说明

岛屿、沙岸、码头和布景由本练习的 Unity 编辑器脚本生成。棚体与色板贴图由随附的脚本和 Blender 源文件生成。Unity 与 URP 为外部运行依赖，包内只包含练习制作的资产和 Unity 序列化项目文件。
