using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

public static class ShelterCapture
{
    public static void BuildAndVerify()
    {
        ShelterPipeline.Prepare();
        ShelterExercise.BuildStarter();
        ShelterExercise.BuildReference();
        ShelterExercise.CheckStarter();
        ShelterExercise.CheckStarterRejected();
        ShelterExercise.CheckReferenceAfterReimport();
    }

    public static void BuildVerifyCapture()
    {
        BuildAndVerify();
        CaptureScenes();
    }

    public static void VerifyShippedScenes()
    {
        EditorSceneManager.OpenScene("Assets/FishingShelter/Scenes/Shelter_Starter.unity", OpenSceneMode.Single);
        ShelterExercise.CheckStarter();
        ShelterExercise.CheckStarterRejected();
        ShelterExercise.CheckReferenceAfterReimport();
    }
    public static void CheckExtendedRoof()
    {
        EditorSceneManager.OpenScene("Assets/FishingShelter/Scenes/Shelter_Reference.unity", OpenSceneMode.Single);
        AssetDatabase.ImportAsset("Assets/FishingShelter/Models/Shelter_LOD0.fbx",
            ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
        var zone = GameObject.Find("Shelter Berths");
        if (!zone || zone.transform.childCount != 3)
            throw new InvalidOperationException("Expected three berths in the reimport check.");
        foreach (Transform shelter in zone.transform)
        {
            float width = 0;
            foreach (MeshFilter filter in shelter.GetComponentsInChildren<MeshFilter>())
                if (filter.sharedMesh && filter.sharedMesh.name == "Roof_LOD0")
                    width = filter.GetComponent<Renderer>().bounds.size.x;
            if (Mathf.Abs(width - 3.18f) > 0.04f)
                throw new InvalidOperationException($"Re-exported roof width at {shelter.name} was {width:F3}.");
            Debug.Log($"AGDS_ISLAND_ROOF_REIMPORT berth={shelter.name} width={width:F3}");
        }
    }

    public static void CaptureScenes()
    {
        string evidence = Environment.GetEnvironmentVariable("AGDS_ISLAND_EVIDENCE");
        if (string.IsNullOrWhiteSpace(evidence) || !Directory.Exists(evidence))
            throw new InvalidOperationException("Set AGDS_ISLAND_EVIDENCE to an existing output directory.");

        Capture("Shelter_Starter", Path.Combine(evidence, "01-starter.png"));
        Capture("Shelter_Reference", Path.Combine(evidence, "02-reference.png"));
    }

    private static void Capture(string sceneName, string path)
    {
        Scene scene = EditorSceneManager.OpenScene($"Assets/FishingShelter/Scenes/{sceneName}.unity", OpenSceneMode.Single);
        Camera camera = Camera.main;
        if (!camera || camera.gameObject.scene != scene)
            throw new InvalidOperationException($"Scene {sceneName} has no main camera.");

        var target = new RenderTexture(1280, 800, 24, RenderTextureFormat.ARGB32);
        var texture = new Texture2D(1280, 800, TextureFormat.RGB24, false);
        RenderTexture previous = RenderTexture.active;
        try
        {
            var request = new UniversalRenderPipeline.SingleCameraRequest { destination = target };
            if (!RenderPipeline.SupportsRenderRequest(camera, request))
                throw new InvalidOperationException("Current URP renderer does not support a camera capture.");
            RenderPipeline.SubmitRenderRequest(camera, request);
            // The first request warms URP's scene and per-material state in a fresh batch editor.
            RenderPipeline.SubmitRenderRequest(camera, request);
            RenderTexture.active = target;
            texture.ReadPixels(new Rect(0, 0, 1280, 800), 0, 0, false);
            texture.Apply(false);
            File.WriteAllBytes(path, texture.EncodeToPNG());
            Debug.Log($"AGDS_ISLAND_CAPTURE {sceneName}");
        }
        finally
        {
            RenderTexture.active = previous;
            UnityEngine.Object.DestroyImmediate(texture);
            UnityEngine.Object.DestroyImmediate(target);
        }
    }
}
