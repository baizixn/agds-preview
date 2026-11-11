# Unity 静态资产只读接收（按需）

仅在当前任务需要接收已导入的静态 FBX/Prefab，并已取得项目自己的尺寸、方向依据、材质预期和容差时，由 engineering 选择使用。普通编码、非资产任务、其他引擎任务不需要本检查器；没有新增角色、全局流程或强制验收门。

## 先取得要求，再测量

从项目已批准资料/交接取要求，明确测量对象、米单位、坐标、容差；不能把检查器实际读数反抄成期望值。方向需要可信标记与来源或作者明确约定；对称、无依据或缺少可定位标记时保持 Unknown，不凭 Transform 旋转数值猜。材质须指明每个 Renderer/槽位、shader 和需比较的属性含义。

先在获准的隔离 Unity 工程首次导入资产；将本 Skill 的 `scripts/unity-static-asset-receiver/Receiver.cs` 复制到该工程 `Assets/Editor/Receiver.cs`。这是准备动作，会创建脚本及 meta；不属于检查器只读运行。检查器文件原始 SHA256 为 `9157ee099079a75229184885cf7bd1bd92288bd49b4d4d2268c4180fe03112a8`。不用修改原代码，也不调用任何资产修复操作。

## 输入合同

写一份项目外绝对路径 JSON。字段区分大小写；schemaVersion=1，assetPath 为规范的 `Assets/...fbx` 或 `.prefab`，dependencyFingerprint 绑定输入文件身份。其余三组要求缺失为 Unknown，不假通过。

| 字段 | 含义 |
| --- | --- |
| dimensions | unit=`m`，frame=`asset-parent`，size 的 x/y/z 为期望米数，tolerance 为各轴绝对误差 |
| direction | origin/front/up 为相对资产根的标记路径；expectedForward/expectedUp 为非零正交向量；toleranceDegrees 小于90；provenance 说明标记与几何特征/作者约定的可信来源 |
| materials | colorSpace 与工程一致；encoding=`shader-property-raw`；slots 完整映射所有实际材质槽 |
| 每个 slot | renderer 相对路径（根用`.`）、slot 从0起、shader、properties |
| 每个 property | name、kind、非负 tolerance；float 要 value，color 要 color 的 r/g/b/a |

尺寸测量包含资产根与内部祖先的全部变换，取所有静态 MeshRenderer（含 inactive）的真实顶点 AABB；1 Unity单位按合同为1米，独立于打开的场景。不是文件元数据、局部 mesh bounds、Collider 或完整造型质量检查。

材质只支持 `Universal Render Pipeline/Lit` 的 `_BaseColor`/color、`_Metallic`/float、`_Smoothness`/float。比较 Material.GetColor/GetFloat 的原始 shader 存储数值，不自动做 sRGB/Linear 转换。材质名不参与判断；数值通过不证明贴图、关键词、透明模式、渲染状态或外观一致。

以下只是字段形状示例；数字与路径均为虚构演示，必须由任务要求替换，不能作为项目默认标准或用于自动生成预期：

```json
{
  "schemaVersion": 1,
  "assetPath": "Assets/Incoming/Example.prefab",
  "dependencyFingerprint": "UNBOUND",
  "dimensions": {"unit":"m","frame":"asset-parent","size":{"x":1,"y":2,"z":3},"tolerance":0.001},
  "direction": {"origin":"Origin","front":"Front","up":"Up","expectedForward":{"x":0,"y":0,"z":1},"expectedUp":{"x":0,"y":1,"z":0},"toleranceDegrees":0.1,"provenance":"Replace with reviewed authoring evidence"},
  "materials": {"colorSpace":"Linear","encoding":"shader-property-raw","slots":[
    {"renderer":"Body","slot":0,"shader":"Universal Render Pipeline/Lit","properties":[
      {"name":"_BaseColor","kind":"color","color":{"r":0.5,"g":0.5,"b":0.5,"a":1},"tolerance":0.0001},
      {"name":"_Metallic","kind":"float","value":0,"tolerance":0.0001},
      {"name":"_Smoothness","kind":"float","value":0.5,"tolerance":0.0001}
    ]}
  ]}
}
```

## 明确绑定输入身份

完成独立要求与输入审查后，才绑定 dependencyFingerprint。可先用 `UNBOUND` 调用一次，报告 identity=Fail 并在 actual 给出实际指纹；该次不是验收通过。核实确为所审查输入后，显式把指纹填入合同，再检查。只绑定文件身份，不能据报告改尺寸/方向/材质预期。资产、依赖或 importer meta 改变后，先重新确认输入与要求；工具不会偷偷重绑或自动更新合同。

也可在获准的 Editor 脚本中读取 `AgdsAssetReceiver.Receiver.Fingerprint("Assets/Incoming/Example.prefab")`。算法为 AssetDatabase.GetDependencies(assetPath,true) 中所有 Assets/ 文件及存在的对应 .meta；最终路径按 Ordinal 排序，每项 `path\t小写SHA256\n`，拼接UTF-8再取SHA256。包兼容性由单独环境门检查，不在此文件指纹内。

## 最短调用

```powershell
& '<Unity绝对路径>/Unity.exe' -batchmode -nographics -quit `
  -projectPath '<获准Unity工程绝对路径>' `
  -executeMethod AgdsAssetReceiver.Receiver.Run `
  -receiverRequirements '<项目外要求JSON绝对路径>' `
  -receiverOutputDir '<项目外明确报告目录绝对路径>' `
  -receiverReportName 'receipt.json' `
  -logFile '<项目外Unity日志绝对路径>'
```

OutputDir 必须为工程外绝对目录，不经 symlink/junction；文件名仅简单 `.json`，拒绝覆盖现物。重复换新目录/文件名。Editor 调用者可用 `Receiver.RunFile(requirementsPath, outputDirectory, reportName)`，返回同一 Report。

读报告 overall 与 checks 的 expected、actual、target、message，不能把 Unity 退出0当作资产通过。只有所需检查全部 Pass 才整体 Pass；Fail、Unknown、Unsupported 分别是明确不符、依据缺失/歧义、超出支持范围。存在多个状态时 Fail 优先，其后 Unsupported、Unknown；逐项状态仍保留。

## 已证范围与只读边界

已验证 Unity 6000.5.10f1 + URP17.5.0 + Linear；静态 FBX/Prefab 层级仅 Transform、MeshFilter、MeshRenderer。其他 Unity版本/包、Gamma、动画、SkinnedMesh、脚本、运行时、设备、性能和完整美术验收没有本次证据。

检查器不修改资产/meta/importer、材质、Prefab、Scene、ProjectSettings，不缩放、旋转、重分配或重导入；只写明确外部报告。首次准备与 Unity 自身 Library/Logs 等缓存写入需分开记录。在需只读证据的任务中，外部调用者对 Assets、Packages、ProjectSettings（含meta）做检查前后哈希，不让被测逻辑自报通过代替证明。
