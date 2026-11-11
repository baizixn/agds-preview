using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

public static class ShelterExercise
{
    private const string Root = "Assets/FishingShelter";
    private const string StarterScene = Root + "/Scenes/Shelter_Starter.unity";
    private const string ReferenceScene = Root + "/Scenes/Shelter_Reference.unity";
    private const string PrefabPath = Root + "/Prefabs/Shelter.prefab";
    private const string MaterialPath = Root + "/Materials/Shelter.mat";
    private const string TexturePath = Root + "/Models/ShelterPalette.png";
    private const string Lod0Path = Root + "/Models/Shelter_LOD0.fbx";
    private const string Lod1Path = Root + "/Models/Shelter_LOD1.fbx";
    private const string ZoneName = "Shelter Berths";
    private const string LitShader = "Universal Render Pipeline/Lit";
    private static readonly float[] BerthOffsets = { -4f, 0f, 4f };

    [MenuItem("AGDS/Shelter Exercise/Build Starter")]
    public static void BuildStarter()
    {
        BuildScene(StarterScene, zone =>
        {
            Material timber = LoadRequired<Material>(Root + "/Materials/Timber.mat");
            Material foliage = LoadRequired<Material>(Root + "/Materials/Foliage.mat");
            for (int index = 0; index < BerthOffsets.Length; index++)
            {
                Vector3 berth = new Vector3(BerthOffsets[index], 0f, 0f);
                Cube("Loose rear wall " + (index + 1), zone, berth + new Vector3(0f, 1f, 0.9f),
                    new Vector3(3f, 2f, 0.2f), timber, true);
                Cube("Loose roof " + (index + 1), zone, berth + new Vector3(0f, 2.1f, 0f),
                    new Vector3(3.1f, 0.2f, 2f), foliage, true);
                Cube("Loose side " + (index + 1), zone, berth + new Vector3(-1.4f, 1f, 0f),
                    new Vector3(0.2f, 2f, 1.9f), timber, true);
                if (index == 1)
                {
                    Cube("Doorway obstruction", zone, berth + new Vector3(0f, 0.55f, -1f),
                        new Vector3(1f, 1.1f, 0.3f), timber, true);
                }
            }
        });
        Debug.Log("AGDS_SHELTER_BUILD mode=starter status=PASS path=" + StarterScene);
    }

    [MenuItem("AGDS/Shelter Exercise/Build Reference")]
    public static void BuildReference()
    {
        GameObject high = LoadRequired<GameObject>(Lod0Path);
        GameObject low = LoadRequired<GameObject>(Lod1Path);
        Texture2D palette = LoadRequired<Texture2D>(TexturePath);
        var importer = AssetImporter.GetAtPath(TexturePath) as TextureImporter;
        Require(importer != null, "Expected a TextureImporter at " + TexturePath);
        if (importer.maxTextureSize != 1024)
        {
            importer.maxTextureSize = 1024;
            importer.SaveAndReimport();
            palette = LoadRequired<Texture2D>(TexturePath);
        }

        Material material = UpdateMaterial(MaterialPath, Color.white, palette);
        EnsureFolder(Root + "/Prefabs");
        BuildScene(ReferenceScene, zone =>
        {
            var source = new GameObject("Shelter");
            try
            {
                Renderer[] highRenderers = AddModel(source.transform, high, "LOD0", material);
                Renderer[] lowRenderers = AddModel(source.transform, low, "LOD1", material);
                var lodGroup = source.AddComponent<LODGroup>();
                lodGroup.SetLODs(new[] { new LOD(0.11f, highRenderers), new LOD(0.035f, lowRenderers) });
                lodGroup.RecalculateBounds();

                AddBox(source, new Vector3(0f, 1.1f, 0.9f), new Vector3(3f, 2.2f, 0.2f));
                AddBox(source, new Vector3(-1.4f, 1.1f, 0f), new Vector3(0.2f, 2.2f, 1.8f));
                AddBox(source, new Vector3(1.4f, 1.1f, 0f), new Vector3(0.2f, 2.2f, 1.8f));

                GameObject prefab = PrefabUtility.SaveAsPrefabAsset(source, PrefabPath, out bool saved);
                Require(saved && prefab != null, "Could not save " + PrefabPath);
                for (int index = 0; index < BerthOffsets.Length; index++)
                {
                    var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, zone);
                    instance.name = "Shelter " + (index + 1);
                    instance.transform.localPosition = new Vector3(BerthOffsets[index], 0f, 0f);
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(source);
            }
        });

        Debug.Log("AGDS_SHELTER_BUILD mode=reference status=PASS path=" + ReferenceScene);
    }

    public static void CheckStarter()
    {
        CheckSavedScene(StarterScene, CheckStarterScene);
    }

    public static void CheckReference()
    {
        CheckSavedScene(ReferenceScene, CheckReferenceScene);
    }

    public static void CheckReferenceAfterReimport()
    {
        foreach (string path in new[] { Lod0Path, Lod1Path, TexturePath })
        {
            LoadRequired<UnityEngine.Object>(path);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
        }
        CheckReference();
        Debug.Log("AGDS_SHELTER_REIMPORT status=PASS modelAssets=2 textureAssets=1");
    }

    [MenuItem("AGDS/Shelter Exercise/Check Active Scene")]
    public static void CheckActiveScene()
    {
        Scene scene = SceneManager.GetActiveScene();
        if (scene.path == StarterScene)
        {
            CheckStarterScene(scene);
            return;
        }
        if (scene.path == ReferenceScene)
        {
            CheckReferenceScene(scene);
            return;
        }
        throw new InvalidOperationException("Open Shelter_Starter or Shelter_Reference before checking.");
    }

    [MenuItem("AGDS/Shelter Exercise/Check Delivery")]
    public static void CheckDelivery()
    {
        CheckReferenceScene(SceneManager.GetActiveScene());
    }

    public static void CheckStarterRejected()
    {
        CheckSavedScene(StarterScene, scene =>
        {
            try
            {
                CheckReferenceScene(scene);
            }
            catch (InvalidOperationException failure) when (failure.Message == "AGDS_SHELTER_FAILURE Expected exactly three shelter roots.")
            {
                Debug.Log("AGDS_SHELTER_ACCEPTANCE starter=REJECTED reason=loose_scene_objects");
                return;
            }
            throw new InvalidOperationException("The delivery check unexpectedly accepted the starter.");
        });
    }

    private static void BuildScene(string path, Action<Transform> populate)
    {
        EnsureFolder(Root + "/Scenes");
        Scene previous = SceneManager.GetActiveScene();
        Scene existing = SceneManager.GetSceneByPath(path);
        Require(!existing.IsValid() || !existing.isLoaded,
            "Close the generated scene before rebuilding it: " + path);
        bool additively = previous.IsValid() && previous.isLoaded && !string.IsNullOrEmpty(previous.path);
        Require(additively || !previous.isDirty, "Save the modified untitled scene before building the exercise.");
        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,
            additively ? NewSceneMode.Additive : NewSceneMode.Single);
        SceneManager.SetActiveScene(scene);
        try
        {
            AddIsland();
            var zone = new GameObject(ZoneName);
            populate(zone.transform);
            Require(EditorSceneManager.SaveScene(scene, path), "Could not save " + path);
        }
        finally
        {
            if (additively)
            {
                SceneManager.SetActiveScene(previous);
                EditorSceneManager.CloseScene(scene, true);
            }
        }
    }

    private static void AddIsland()
    {
        var landscape = new GameObject("First Island");
        Material water = UpdateMaterial(Root + "/Materials/Water.mat", new Color(0.052f, 0.245f, 0.27f));
        Material sand = UpdateMaterial(Root + "/Materials/Sand.mat", new Color(0.60f, 0.51f, 0.39f));
        Material timber = UpdateMaterial(Root + "/Materials/Timber.mat", new Color(0.32f, 0.20f, 0.12f));
        Material path = UpdateMaterial(Root + "/Materials/Path.mat", new Color(0.42f, 0.36f, 0.28f));
        Material stone = UpdateMaterial(Root + "/Materials/Stone.mat", new Color(0.29f, 0.39f, 0.39f));
        Material foliage = UpdateMaterial(Root + "/Materials/Foliage.mat", new Color(0.27f, 0.45f, 0.28f));
        Material shallows = UpdateMaterial(Root + "/Materials/Shallows.mat", new Color(0.09f, 0.31f, 0.325f));

        Cube("Water", landscape.transform, new Vector3(0f, -0.65f, 0f), new Vector3(52f, 0.2f, 38f),
            water, false);
        IslandSurface("Shallows", landscape.transform, shallows, 1.085f, -0.53f, -0.54f);
        IslandSurface("Shoreline", landscape.transform, sand, 1f, 0f, -0.75f);

        GameObject floor = Cube("Island floor", landscape.transform, new Vector3(0f, -0.35f, 0f),
            new Vector3(12.5f, 0.7f, 7.5f), sand, true);
        floor.GetComponent<MeshRenderer>().enabled = false;

        for (int index = 0; index < 10; index++)
        {
            Cube("Dock plank", landscape.transform, new Vector3(0f, -0.10f, -6.15f - 0.28f * index),
                new Vector3(2.10f, 0.18f, 0.25f), timber, false);
        }
        foreach (float offset in new[] { -0.95f, 0.95f })
        {
            Cube("Mooring post", landscape.transform, new Vector3(offset, -0.14f, -8.5f),
                new Vector3(0.19f, 1.12f, 0.19f), timber, false);
        }

        Cube("Dock supply crate", landscape.transform, new Vector3(-0.68f, 0.21f, -7.28f),
            new Vector3(0.50f, 0.43f, 0.58f), timber, false);
        Cube("Crate lid", landscape.transform, new Vector3(-0.68f, 0.44f, -7.28f),
            new Vector3(0.55f, 0.075f, 0.63f), path, false);
        Cube("Dock cleat", landscape.transform, new Vector3(0.73f, 0.065f, -8.11f),
            new Vector3(0.30f, 0.14f, 0.16f), stone, false);

        for (int index = 0; index < 7; index++)
        {
            float x = 0.28f * Mathf.Sin(0.76f * index);
            AddSteppingStone(landscape.transform, path, x, -5.85f + 0.52f * index, index);
        }
        for (int index = 0; index < 17; index++)
        {
            float x = -4.42f + 0.55f * index;
            float z = -2.65f + 0.30f * Mathf.Sin(0.63f * index - 0.6f);
            AddSteppingStone(landscape.transform, path, x, z, index);
        }
        foreach (float offset in BerthOffsets)
        {
            AddSteppingStone(landscape.transform, path, offset + 0.10f, -1.77f, 4);
            AddSteppingStone(landscape.transform, path, offset, -1.29f, 7);
        }

        Material ripple = UpdateMaterial(Root + "/Materials/Ripple.mat", new Color(0.20f, 0.43f, 0.43f));
        AddRipple(landscape.transform, ripple, new Vector3(-3.70f, -0.535f, -7.10f), 0.95f, -14f);
        AddRipple(landscape.transform, ripple, new Vector3(-3.28f, -0.535f, -7.53f), 0.57f, -14f);
        AddRipple(landscape.transform, ripple, new Vector3(3.72f, -0.535f, -6.71f), 0.73f, 10f);
        AddRipple(landscape.transform, ripple, new Vector3(5.12f, -0.535f, -6.04f), 1.13f, 17f);
        AddRipple(landscape.transform, ripple, new Vector3(5.36f, -0.535f, -6.40f), 0.58f, 17f);

        AddBeachGrass(landscape.transform, foliage, new Vector3(-4.83f, 0f, -4.28f), 0.28f);
        AddBeachGrass(landscape.transform, foliage, new Vector3(-5.56f, 0f, -3.65f), 0.34f);
        AddBeachGrass(landscape.transform, foliage, new Vector3(5.05f, 0f, -3.67f), 0.30f);
        AddBeachGrass(landscape.transform, foliage, new Vector3(5.75f, 0f, -2.84f), 0.24f);
        AddBeachGrass(landscape.transform, foliage, new Vector3(1.95f, 0f, -5.15f), 0.28f);

        AddRock(landscape.transform, stone, new Vector3(-5.3f, 0.05f, -3.9f), new Vector3(1.12f, 0.60f, 0.77f));
        AddRock(landscape.transform, stone, new Vector3(-5.9f, 0.01f, -3.53f), new Vector3(0.62f, 0.40f, 0.55f));
        AddRock(landscape.transform, stone, new Vector3(5.3f, 0.02f, -3.3f), new Vector3(1.16f, 0.67f, 0.79f));
        AddRock(landscape.transform, stone, new Vector3(5.9f, 0.02f, -3.02f), new Vector3(0.58f, 0.34f, 0.53f));

        AddCoastalTree(landscape.transform, timber, foliage, new Vector3(-5.9f, 0f, 2.3f), 1f);
        AddCoastalTree(landscape.transform, timber, foliage, new Vector3(-4.75f, 0f, 3.15f), 0.73f);
        AddCoastalTree(landscape.transform, timber, foliage, new Vector3(5.55f, 0f, 2.42f), 0.83f);

        var cameraObject = new GameObject("Island Camera");
        Camera camera = cameraObject.AddComponent<Camera>();
        camera.tag = "MainCamera";
        camera.orthographic = true;
        camera.orthographicSize = 7.5f;
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(0.48f, 0.70f, 0.79f);
        cameraObject.transform.position = new Vector3(7f, 13f, -18f);
        cameraObject.transform.LookAt(new Vector3(0f, 0f, -0.65f));

        var sun = new GameObject("Sun").AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.intensity = 1.03f;
        sun.shadows = LightShadows.Soft;
        sun.transform.rotation = Quaternion.Euler(47f, -32f, 0f);
        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(0.65f, 0.71f, 0.75f);
        RenderSettings.sun = sun;
    }

    private static void IslandSurface(string name, Transform parent, Material material, float scale,
        float topHeight, float lowerHeight)
    {
        const int segments = 40;
        EnsureFolder(Root + "/Environment");
        string assetPath = Root + "/Environment/" + name + ".asset";
        Mesh mesh = AssetDatabase.LoadAssetAtPath<Mesh>(assetPath);
        if (mesh == null)
        {
            mesh = new Mesh { name = name };
            AssetDatabase.CreateAsset(mesh, assetPath);
        }
        mesh.Clear();
        var vertices = new Vector3[1 + 2 * segments];
        var triangles = new List<int>(9 * segments);
        vertices[0] = new Vector3(0f, topHeight, 0f);
        for (int index = 0; index < segments; index++)
        {
            float angle = Mathf.PI * 2f * index / segments;
            float radius = 1f + 0.055f * Mathf.Sin(angle * 3f + 0.75f) + 0.034f * Mathf.Cos(angle * 5f - 0.3f);
            float x = 8.2f * scale * radius * Mathf.Cos(angle);
            float z = 6.05f * scale * radius * Mathf.Sin(angle);
            int upper = index + 1;
            int nextUpper = (index + 1) % segments + 1;
            int lower = upper + segments;
            int nextLower = nextUpper + segments;
            vertices[upper] = new Vector3(x, topHeight, z);
            vertices[lower] = new Vector3(1.1f * x, lowerHeight, 1.1f * z);
            triangles.AddRange(new[] { 0, nextUpper, upper, upper, nextUpper, lower, nextUpper, nextLower, lower });
        }
        mesh.vertices = vertices;
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        EditorUtility.SetDirty(mesh);
        AssetDatabase.SaveAssetIfDirty(mesh);

        var surface = new GameObject(name, typeof(MeshFilter), typeof(MeshRenderer));
        surface.transform.SetParent(parent, false);
        surface.GetComponent<MeshFilter>().sharedMesh = mesh;
        surface.GetComponent<MeshRenderer>().sharedMaterial = material;
    }

    private static void AddSteppingStone(Transform parent, Material material, float x, float z, int index)
    {
        float width = 0.57f + 0.08f * Mathf.Sin(index * 2.1f);
        GameObject step = AddRock(parent, material, new Vector3(x, 0.002f, z),
            new Vector3(width, 0.034f, 0.37f), "Stepping stone");
        step.transform.localRotation = Quaternion.Euler(0f, 22f * Mathf.Sin(index * 1.6f), 0f);
    }

    private static void AddRipple(Transform parent, Material material, Vector3 position, float length, float angle)
    {
        GameObject ripple = AddRock(parent, material, position, new Vector3(length, 0.012f, 0.085f), "Sea ripple");
        ripple.transform.localRotation = Quaternion.Euler(0f, angle, 0f);
    }

    private static void AddBeachGrass(Transform parent, Material material, Vector3 position, float height)
    {
        for (int index = -1; index <= 1; index++)
        {
            float bladeHeight = height - 0.06f * Mathf.Abs(index);
            GameObject blade = Cube("Beach grass", parent,
                position + new Vector3(0.065f * index, bladeHeight * 0.44f, 0f),
                new Vector3(0.043f, bladeHeight, 0.04f), material, false);
            blade.transform.localRotation = Quaternion.Euler(8f * index, 0f, -21f * index);
        }
    }

    private static GameObject AddRock(Transform parent, Material material, Vector3 position, Vector3 scale, string name = "Shore rock")
    {
        GameObject rock = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        rock.name = name;
        rock.transform.SetParent(parent, false);
        rock.transform.localPosition = position;
        rock.transform.localRotation = Quaternion.Euler(15f, 32f, -20f);
        rock.transform.localScale = scale;
        rock.GetComponent<MeshRenderer>().sharedMaterial = material;
        UnityEngine.Object.DestroyImmediate(rock.GetComponent<SphereCollider>());
        return rock;
    }

    private static void AddCoastalTree(Transform parent, Material timber, Material foliage, Vector3 position, float scale)
    {
        var tree = new GameObject("Coastal tree");
        tree.transform.SetParent(parent, false);
        tree.transform.localPosition = position;
        tree.transform.localScale = Vector3.one * scale;
        Cube("Trunk", tree.transform, new Vector3(0f, 0.59f, 0f), new Vector3(0.17f, 1.18f, 0.17f),
            timber, false);
        GameObject crown = Cube("Crown", tree.transform, new Vector3(0f, 1.23f, 0f),
            new Vector3(0.8f, 0.87f, 0.8f), foliage, false);
        crown.transform.localRotation = Quaternion.Euler(18f, 38f, 29f);
        GameObject top = Cube("Upper crown", tree.transform, new Vector3(0.13f, 1.67f, 0.04f),
            new Vector3(0.54f, 0.66f, 0.53f), foliage, false);
        top.transform.localRotation = Quaternion.Euler(27f, 14f, 34f);
    }

    private static GameObject Cube(string name, Transform parent, Vector3 position, Vector3 size,
        Material material, bool keepCollider)
    {
        GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = name;
        cube.transform.SetParent(parent, false);
        cube.transform.localPosition = position;
        cube.transform.localScale = size;
        if (material != null)
            cube.GetComponent<MeshRenderer>().sharedMaterial = material;
        if (!keepCollider)
            UnityEngine.Object.DestroyImmediate(cube.GetComponent<BoxCollider>());
        return cube;
    }

    private static Renderer[] AddModel(Transform parent, GameObject asset, string name, Material material)
    {
        var instance = (GameObject)PrefabUtility.InstantiatePrefab(asset, parent);
        instance.name = name;
        var renderers = instance.GetComponentsInChildren<MeshRenderer>(true);
        Require(renderers.Length > 0, "No mesh renderers in " + AssetDatabase.GetAssetPath(asset));
        foreach (MeshRenderer renderer in renderers)
        {
            Material[] slots = renderer.sharedMaterials;
            Require(slots.Length > 0, "No material slots on " + renderer.name);
            for (int slot = 0; slot < slots.Length; slot++)
                slots[slot] = material;
            renderer.sharedMaterials = slots;
        }
        return renderers;
    }

    private static void AddBox(GameObject root, Vector3 center, Vector3 size)
    {
        var box = root.AddComponent<BoxCollider>();
        box.center = center;
        box.size = size;
    }

    private static Material UpdateMaterial(string assetPath, Color tint, Texture2D texture = null)
    {
        Shader shader = Shader.Find(LitShader);
        Require(shader != null, "Universal Render Pipeline Lit shader is unavailable. Install URP first.");
        EnsureFolder(Root + "/Materials");
        var material = AssetDatabase.LoadAssetAtPath<Material>(assetPath);
        if (material == null)
        {
            material = new Material(shader);
            AssetDatabase.CreateAsset(material, assetPath);
        }

        material.shader = shader;
        material.SetColor("_BaseColor", tint);
        material.SetTexture("_BaseMap", texture);
        material.SetFloat("_Smoothness", 0.17f);
        EditorUtility.SetDirty(material);
        AssetDatabase.SaveAssetIfDirty(material);
        return material;
    }

    private static void CheckSavedScene(string path, Action<Scene> inspect)
    {
        LoadRequired<SceneAsset>(path);
        Scene alreadyLoaded = SceneManager.GetSceneByPath(path);
        if (alreadyLoaded.IsValid() && alreadyLoaded.isLoaded)
        {
            inspect(alreadyLoaded);
            return;
        }

        Scene previous = SceneManager.GetActiveScene();
        Scene opened = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
        try
        {
            inspect(opened);
        }
        finally
        {
            if (previous.IsValid() && previous.isLoaded)
                SceneManager.SetActiveScene(previous);
            EditorSceneManager.CloseScene(opened, true);
        }
    }

    private static void CheckStarterScene(Scene scene)
    {
        Transform zone = GetZone(scene);
        GameObject[] directObjects = zone.Cast<Transform>().Select(child => child.gameObject).ToArray();
        int looseCubes = directObjects.Count(obj => obj.GetComponent<MeshRenderer>() != null &&
            !PrefabUtility.IsPartOfPrefabInstance(obj));
        int prefabRoots = directObjects.Count(PrefabUtility.IsAnyPrefabInstanceRoot);
        Collider[] colliders = zone.GetComponentsInChildren<Collider>(true);
        Physics.SyncTransforms();

        int blocked = BerthOffsets.Count(offset => HitAny(colliders, offset, 1.25f));
        int lodGroups = zone.GetComponentsInChildren<LODGroup>(true).Length;
        Debug.Log($"AGDS_SHELTER_FINDINGS looseCubes={looseCubes} prefabRoots={prefabRoots} " +
            $"blockedDoorways={blocked} lodGroups={lodGroups}");
        Require(looseCubes >= 9, "Starter should show loose cube construction.");
        Require(prefabRoots == 0 && lodGroups == 0, "Starter should have no prefabs or LOD groups.");
        Require(blocked == 1 && HitAny(colliders, 0f, 1.25f), "Starter should have one blocked central doorway.");
        Debug.Log("AGDS_SHELTER_CHECK mode=starter status=PASS");
    }

    private static void CheckReferenceScene(Scene scene)
    {
        Transform zone = GetZone(scene);
        GameObject prefab = LoadRequired<GameObject>(PrefabPath);
        Material material = LoadRequired<Material>(MaterialPath);
        Texture2D texture = LoadRequired<Texture2D>(TexturePath);
        var importer = AssetImporter.GetAtPath(TexturePath) as TextureImporter;
        Require(material.shader != null && material.shader.name == LitShader &&
            material.GetTexture("_BaseMap") == texture, "Shared material must use URP Lit and the imported palette.");
        Require(importer != null && importer.maxTextureSize == 1024 && texture.width <= 1024 &&
            texture.height <= 1024, "Palette must import at a maximum size of 1024.");
        Require(zone.childCount == BerthOffsets.Length, "Expected exactly three shelter roots.");
        Physics.SyncTransforms();

        long highTriangles = 0;
        long lowTriangles = 0;
        for (int index = 0; index < BerthOffsets.Length; index++)
        {
            float offset = BerthOffsets[index];
            Transform shelter = zone.GetChild(index);
            Require(PrefabUtility.IsAnyPrefabInstanceRoot(shelter.gameObject) &&
                PrefabUtility.GetCorrespondingObjectFromSource(shelter.gameObject) == prefab,
                "Berth " + (index + 1) + " must be an instance of the canonical Shelter prefab.");
            Require(Vector3.Distance(shelter.position, new Vector3(offset, 0f, 0f)) < 0.001f &&
                Quaternion.Angle(shelter.rotation, Quaternion.identity) < 0.01f &&
                Vector3.Distance(shelter.lossyScale, Vector3.one) < 0.001f,
                "Berth " + (index + 1) + " position, rotation, or scale has drifted.");

            var group = shelter.GetComponent<LODGroup>();
            Require(group != null && shelter.GetComponentsInChildren<LODGroup>(true).Length == 1,
                "Each shelter needs exactly one root LODGroup.");
            LOD[] lods = group.GetLODs();
            Require(group.enabled && lods.Length == 2 && lods[0].screenRelativeTransitionHeight >
                lods[1].screenRelativeTransitionHeight && lods[1].screenRelativeTransitionHeight > 0f,
                "LOD0 and LOD1 must be ordered and enabled.");
            highTriangles = CountLodTriangles(lods[0].renderers, Lod0Path, material);
            lowTriangles = CountLodTriangles(lods[1].renderers, Lod1Path, material);
            Require(highTriangles > 0 && highTriangles <= 1500 && lowTriangles > 0 &&
                lowTriangles <= 600 && lowTriangles < highTriangles,
                $"LOD triangle budget exceeded or LOD1 is not simpler: LOD0={highTriangles}, LOD1={lowTriangles}.");
            var registered = new HashSet<Renderer>(lods[0].renderers.Concat(lods[1].renderers));
            Require(registered.Count == lods[0].renderers.Length + lods[1].renderers.Length &&
                registered.SetEquals(shelter.GetComponentsInChildren<Renderer>(true)),
                "Every shelter renderer must belong to exactly one LOD.");

            Collider[] colliders = shelter.GetComponentsInChildren<Collider>(true);
            Require(colliders.Length == 3 && colliders.All(collider => collider is BoxCollider &&
                collider.transform == shelter && collider.enabled && !collider.isTrigger),
                "Expected three solid primitive box colliders on the shelter root.");
            Require(!HitAny(colliders, offset, 1.25f), "Shelter doorway is obstructed at berth " + (index + 1));
            Require(HitAny(colliders, offset, 3.5f), "Shelter back wall did not block the test ray at berth " + (index + 1));
            Require(HitAny(colliders, new Vector3(offset, 0.65f, 0f), Vector3.left, 2f) &&
                HitAny(colliders, new Vector3(offset, 0.65f, 0f), Vector3.right, 2f),
                "Both shelter side walls must block rays at berth " + (index + 1));
        }

        Debug.Log($"AGDS_SHELTER_CHECK mode=reference status=PASS prefabInstances=3 lod0Triangles={highTriangles} " +
            $"lod1Triangles={lowTriangles} collidersPerShelter=3 clearDoorways=3 blockedBackWalls=3 " +
            $"blockedSideWalls=6 paletteMaxSize={importer.maxTextureSize}");
    }

    private static long CountLodTriangles(Renderer[] renderers, string sourcePath, Material material)
    {
        Require(renderers.Length > 0, "LOD has no renderers for " + sourcePath);
        long triangles = 0;
        foreach (Renderer renderer in renderers)
        {
            Require(renderer is MeshRenderer && renderer.enabled && renderer.gameObject.activeInHierarchy,
                "Expected an enabled and active MeshRenderer for " + sourcePath);
            MeshFilter filter = renderer.GetComponent<MeshFilter>();
            Mesh mesh = filter != null ? filter.sharedMesh : null;
            Require(mesh != null && AssetDatabase.GetAssetPath(mesh) == sourcePath,
                "LOD mesh must come from " + sourcePath);
            Material[] slots = renderer.sharedMaterials;
            Require(slots.Length == mesh.subMeshCount && slots.All(slot => slot == material),
                "All submeshes must use the shared shelter material.");
            for (int index = 0; index < mesh.subMeshCount; index++)
            {
                Require(mesh.GetTopology(index) == MeshTopology.Triangles, "Expected triangle topology.");
                triangles += mesh.GetIndexCount(index) / 3;
            }
        }
        return triangles;
    }

    private static bool HitAny(IEnumerable<Collider> colliders, float offset, float distance)
    {
        return HitAny(colliders, new Vector3(offset, 0.65f, -2f), Vector3.forward, distance);
    }

    private static bool HitAny(IEnumerable<Collider> colliders, Vector3 origin, Vector3 direction, float distance)
    {
        var ray = new Ray(origin, direction);
        return colliders.Any(collider => collider.Raycast(ray, out _, distance));
    }

    private static Transform GetZone(Scene scene)
    {
        GameObject zone = scene.GetRootGameObjects().SingleOrDefault(root => root.name == ZoneName);
        Require(zone != null, "Missing shelter berth zone in " + scene.path);
        return zone.transform;
    }

    private static T LoadRequired<T>(string path) where T : UnityEngine.Object
    {
        T asset = AssetDatabase.LoadAssetAtPath<T>(path);
        Require(asset != null, "Missing or incompatible asset: " + path);
        return asset;
    }

    private static void EnsureFolder(string path)
    {
        if (AssetDatabase.IsValidFolder(path))
            return;
        int separator = path.LastIndexOf('/');
        string parent = path.Substring(0, separator);
        EnsureFolder(parent);
        Require(!string.IsNullOrEmpty(AssetDatabase.CreateFolder(parent, path.Substring(separator + 1))),
            "Could not create asset folder " + path);
    }

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new InvalidOperationException("AGDS_SHELTER_FAILURE " + message);
    }
}
