using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class ShelterPipeline
{
    private const string Folder = "Assets/FishingShelter/Settings";

    public static void Prepare()
    {
        Directory.CreateDirectory(Folder);
        AssetDatabase.Refresh();
        var renderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(Folder + "/IslandRenderer.asset");
        if (!renderer)
        {
            renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
            AssetDatabase.CreateAsset(renderer, Folder + "/IslandRenderer.asset");
        }

        var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(Folder + "/IslandPipeline.asset");
        if (!pipeline)
        {
            pipeline = UniversalRenderPipelineAsset.Create(renderer);
            AssetDatabase.CreateAsset(pipeline, Folder + "/IslandPipeline.asset");
        }

        GraphicsSettings.defaultRenderPipeline = pipeline;
        QualitySettings.renderPipeline = pipeline;
        PlayerSettings.colorSpace = ColorSpace.Linear;
        AssetDatabase.SaveAssets();
    }
}
