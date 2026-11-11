// Candidate: Editor-only static FBX/Prefab receipt. No asset mutation APIs.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Security.Cryptography;
using System.Text;
using Unity.Collections;
using UnityEditor;
using UnityEngine;

namespace AgdsAssetReceiver
{
    [DataContract] public sealed class Requirements
    {
        [DataMember(IsRequired=true)] public int schemaVersion;
        [DataMember(IsRequired=true)] public string assetPath;
        [DataMember(IsRequired=true)] public string dependencyFingerprint;
        [DataMember] public Dimensions dimensions;
        [DataMember] public Direction direction;
        [DataMember] public Materials materials;
    }
    [DataContract] public sealed class Vec
    {
        [DataMember(IsRequired=true)] public double x;
        [DataMember(IsRequired=true)] public double y;
        [DataMember(IsRequired=true)] public double z;
        public Vector3 ToVector() { return new Vector3((float)x,(float)y,(float)z); }
    }
    [DataContract] public sealed class Rgba
    {
        [DataMember(IsRequired=true)] public double r;
        [DataMember(IsRequired=true)] public double g;
        [DataMember(IsRequired=true)] public double b;
        [DataMember(IsRequired=true)] public double a;
    }
    [DataContract] public sealed class Dimensions
    {
        [DataMember(IsRequired=true)] public string unit;
        [DataMember(IsRequired=true)] public string frame;
        [DataMember(IsRequired=true)] public Vec size;
        [DataMember(IsRequired=true)] public double tolerance;
    }
    [DataContract] public sealed class Direction
    {
        [DataMember(IsRequired=true)] public string origin;
        [DataMember(IsRequired=true)] public string front;
        [DataMember(IsRequired=true)] public string up;
        [DataMember(IsRequired=true)] public Vec expectedForward;
        [DataMember(IsRequired=true)] public Vec expectedUp;
        [DataMember(IsRequired=true)] public double toleranceDegrees;
        [DataMember(IsRequired=true)] public string provenance;
    }
    [DataContract] public sealed class Materials
    {
        [DataMember(IsRequired=true)] public string colorSpace;
        [DataMember(IsRequired=true)] public string encoding;
        [DataMember(IsRequired=true)] public Slot[] slots;
    }
    [DataContract] public sealed class Slot
    {
        [DataMember(IsRequired=true)] public string renderer;
        [DataMember(IsRequired=true)] public int slot;
        [DataMember(IsRequired=true)] public string shader;
        [DataMember(IsRequired=true)] public Property[] properties;
    }
    [DataContract] public sealed class Property
    {
        [DataMember(IsRequired=true)] public string name;
        [DataMember(IsRequired=true)] public string kind;
        [DataMember(IsRequired=true)] public double tolerance;
        [DataMember] public double? value;
        [DataMember] public Rgba color;
    }
    [Serializable] public sealed class Check
    {
        public string id, status, target, expected, actual, message;
    }
    [Serializable] public sealed class Report
    {
        public int schemaVersion=1;
        public string overall, assetPath, requirementsSha256, unityVersion, urpVersion, colorSpace;
        public Check[] checks;
    }

    public static class Receiver
    {
        const string Lit="Universal Render Pipeline/Lit";
        static string ProjectRoot { get { return Path.GetFullPath(Path.Combine(Application.dataPath,"..")); } }
        static bool Finite(double v) { return !double.IsNaN(v) && !double.IsInfinity(v) && Math.Abs(v)<=float.MaxValue; }
        static bool Valid(Vec v) { return v!=null && Finite(v.x) && Finite(v.y) && Finite(v.z); }
        static string Json(object v)
        {
            if(v==null) return "null";
            if(!v.GetType().IsDefined(typeof(DataContractAttribute),false)) return JsonUtility.ToJson(v);
            using(var s=new MemoryStream())
            {
                new DataContractJsonSerializer(v.GetType()).WriteObject(s,v);
                return Encoding.UTF8.GetString(s.ToArray());
            }
        }
        static string Number(double v) { return v.ToString("R",CultureInfo.InvariantCulture); }
        static Check C(string id,string status,string target,string expected,string actual,string message="")
        { return new Check {id=id,status=status,target=target,expected=expected,actual=actual,message=message}; }
        static string Status(IEnumerable<Check> checks)
        {
            var a=checks.ToArray();
            if(a.Any(c=>c.status=="Fail")) return "Fail";
            if(a.Any(c=>c.status=="Unsupported")) return "Unsupported";
            if(a.Length==0 || a.Any(c=>c.status!="Pass")) return "Unknown";
            return "Pass";
        }
        public static string FileHash(string path)
        {
            using(var sha=SHA256.Create()) using(var s=File.OpenRead(path))
                return BitConverter.ToString(sha.ComputeHash(s)).Replace("-","").ToLowerInvariant();
        }
        // Dependencies in Assets only. Package compatibility is separately checked.
        public static string Fingerprint(string assetPath)
        {
            var files=new SortedSet<string>(StringComparer.Ordinal);
            foreach(var p in AssetDatabase.GetDependencies(assetPath,true).Where(p=>p.StartsWith("Assets/",StringComparison.Ordinal)))
            {
                if(!File.Exists(Path.Combine(ProjectRoot,p))) throw new IOException("Missing dependency: "+p);
                files.Add(p);
                if(File.Exists(Path.Combine(ProjectRoot,p+".meta"))) files.Add(p+".meta");
            }
            if(!files.Contains(assetPath)) throw new IOException("Input not in imported dependency graph");
            var text=new StringBuilder();
            foreach(var p in files) text.Append(p).Append('\t').Append(FileHash(Path.Combine(ProjectRoot,p))).Append('\n');
            using(var sha=SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(text.ToString()))).Replace("-","").ToLowerInvariant();
        }
        static Transform Find(Transform root,string path)
        {
            if(path==".") return root;
            if(string.IsNullOrWhiteSpace(path) || path.StartsWith("/") || path.Split('/').Any(p=>p=="" || p=="." || p=="..")) return null;
            var t=root;
            foreach(var part in path.Split('/'))
            {
                var matches=Enumerable.Range(0,t.childCount).Select(t.GetChild).Where(c=>c.name==part).ToArray();
                if(matches.Length!=1) return null; // Ambiguous names never select silently.
                t=matches[0];
            }
            return t;
        }
        static string Relative(Transform root,Transform t)
        {
            if(t==root) return ".";
            var parts=new List<string>();
            while(t!=root && t!=null) { parts.Add(t.name); t=t.parent; }
            parts.Reverse(); return string.Join("/",parts);
        }
        static Check Size(GameObject root,Dimensions d)
        {
            if(d==null) return C("dimensions","Unknown","all static mesh vertices","explicit dimensions",null,"Missing requirements");
            if(d.unit!="m" || d.frame!="asset-parent") return C("dimensions","Unsupported","frame",Json(d),null,"Only metres in the asset-parent frame (1 Unity unit = 1 m)");
            if(!Valid(d.size) || d.size.x<=0 || d.size.y<=0 || d.size.z<=0 || !Finite(d.tolerance) || d.tolerance<0)
                return C("dimensions","Unknown","requirements",Json(d),null,"Invalid dimensions/tolerance");
            var min=new Vector3(float.PositiveInfinity,float.PositiveInfinity,float.PositiveInfinity);
            var max=new Vector3(float.NegativeInfinity,float.NegativeInfinity,float.NegativeInfinity);
            int count=0;
            foreach(var renderer in root.GetComponentsInChildren<MeshRenderer>(true))
            {
                var mf=renderer.GetComponent<MeshFilter>();
                if(mf==null || mf.sharedMesh==null) return C("dimensions","Unknown",Relative(root.transform,renderer.transform),Json(d),null,"Missing mesh");
                using(var data=MeshUtility.AcquireReadOnlyMeshData(mf.sharedMesh))
                using(var vertices=new NativeArray<Vector3>(data[0].vertexCount,Allocator.Temp))
                {
                    data[0].GetVertices(vertices);
                    var matrix=renderer.transform.localToWorldMatrix;
                    foreach(var local in vertices)
                    {
                        var p=matrix.MultiplyPoint3x4(local);
                        if(!Finite(p.x)||!Finite(p.y)||!Finite(p.z)) return C("dimensions","Unknown","geometry",Json(d),null,"Nonfinite transformed vertex");
                        min=Vector3.Min(min,p); max=Vector3.Max(max,p); count++;
                    }
                }
            }
            if(count==0) return C("dimensions","Unknown","geometry",Json(d),null,"No static mesh vertices");
            var size=max-min;
            bool pass=Math.Abs(size.x-d.size.x)<=d.tolerance && Math.Abs(size.y-d.size.y)<=d.tolerance && Math.Abs(size.z-d.size.z)<=d.tolerance;
            return C("dimensions",pass?"Pass":"Fail","all static MeshRenderers, including inactive",Json(d),Json(size),"Vertex AABB after all root/ancestor transforms; not local mesh bounds");
        }
        static Check Orientation(GameObject root,Direction d)
        {
            if(d==null) return C("direction","Unknown","direction markers","explicit marker contract",null,"No semantic direction supplied");
            if(string.IsNullOrWhiteSpace(d.provenance)||!Valid(d.expectedForward)||!Valid(d.expectedUp)||!Finite(d.toleranceDegrees)||d.toleranceDegrees<0||d.toleranceDegrees>=90)
                return C("direction","Unknown","requirements",Json(d),null,"Invalid marker provenance, axes or tolerance");
            var f=d.expectedForward.ToVector(); var u=d.expectedUp.ToVector();
            if(f.sqrMagnitude<1e-12f||u.sqrMagnitude<1e-12f||Math.Abs(Vector3.Dot(f.normalized,u.normalized))>0.001f)
                return C("direction","Unknown","requirements",Json(d),null,"Expected axes must be nonzero and perpendicular");
            var o=Find(root.transform,d.origin); var ft=Find(root.transform,d.front); var ut=Find(root.transform,d.up);
            if(o==null||ft==null||ut==null) return C("direction","Unknown","marker paths",Json(d),null,"Missing or ambiguous marker; cannot infer from Transform Euler values");
            var af=ft.position-o.position; var au=ut.position-o.position;
            if(af.sqrMagnitude<1e-12f||au.sqrMagnitude<1e-12f||Math.Abs(Vector3.Dot(af.normalized,au.normalized))>0.001f)
                return C("direction","Unknown","marker geometry",Json(d),null,"Degenerate or non-orthogonal marker axes");
            float fa=Vector3.Angle(f,af), ua=Vector3.Angle(u,au);
            return C("direction",fa<=d.toleranceDegrees && ua<=d.toleranceDegrees?"Pass":"Fail","authored marker contract",Json(d),"forward="+Json(af.normalized)+"; up="+Json(au.normalized)+"; anglesDegrees="+Number(fa)+","+Number(ua),"Proves marker agreement only; provenance must tie markers to visible features");
        }
        static void MaterialChecks(GameObject root,Materials m,List<Check> checks)
        {
            var detail=new List<Check>();
            if(m==null || m.slots==null || m.slots.Length==0) detail.Add(C("materials.requirements","Unknown","materials","explicit complete slot mapping",null,"Missing requirements"));
            else if(m.colorSpace!=PlayerSettings.colorSpace.ToString() || m.encoding!="shader-property-raw")
                detail.Add(C("materials.encoding","Unsupported","color encoding",Json(m),PlayerSettings.colorSpace.ToString(),"Only explicit active color space and raw shader property values; no appearance equivalence"));
            else
            {
                var covered=new HashSet<string>(StringComparer.Ordinal);
                foreach(var s in m.slots)
                {
                    if(s==null) { detail.Add(C("materials.slot","Unknown","mapping",null,null,"Null slot requirement")); continue; }
                    string key=s.renderer+"#"+s.slot;
                    var t=Find(root.transform,s.renderer);
                    var renderers=t==null?new Renderer[0]:t.GetComponents<Renderer>();
                    if(!covered.Add(key)||renderers.Length!=1||!(renderers[0] is MeshRenderer)||s.slot<0||s.slot>=renderers[0].sharedMaterials.Length)
                    { detail.Add(C("materials.slot","Unknown",key,Json(s),null,"Duplicate, missing or ambiguous Renderer/slot")); continue; }
                    var mat=renderers[0].sharedMaterials[s.slot];
                    if(mat==null) { detail.Add(C("materials.slot","Fail",key,Json(s),"null","Empty material")); continue; }
                    string actualShader=mat.shader==null?"null":mat.shader.name;
                    if(s.shader!=Lit || actualShader!=Lit)
                    { detail.Add(C("materials.shader",s.shader==Lit?"Fail":"Unsupported",key,s.shader,actualShader,"Supported comparison: URP Lit only")); continue; }
                    if(s.properties==null||s.properties.Length==0) { detail.Add(C("materials.properties","Unknown",key,"explicit properties",null)); continue; }
                    var propertyNames=new HashSet<string>(StringComparer.Ordinal);
                    foreach(var p in s.properties)
                    {
                        if(p==null) { detail.Add(C("materials.property","Unknown",key,null,null,"Null property")); continue; }
                        string target=key+"/"+p.name;
                        if(!propertyNames.Add(p.name??"")||!Finite(p.tolerance)||p.tolerance<0)
                        { detail.Add(C("materials.property","Unknown",target,Json(p),null,"Duplicate property or invalid tolerance")); continue; }
                        if((p.name!="_BaseColor"||p.kind!="color") && ((p.name!="_Metallic"&&p.name!="_Smoothness")||p.kind!="float"))
                        { detail.Add(C("materials.property","Unsupported",target,Json(p),null,"Unsupported shader-property meaning")); continue; }
                        if(!mat.HasProperty(p.name)) { detail.Add(C("materials.property","Fail",target,Json(p),null,"Shader property missing")); continue; }
                        bool pass; string actual;
                        if(p.kind=="float")
                        {
                            if(!p.value.HasValue||!Finite(p.value.Value)) { detail.Add(C("materials.property","Unknown",target,Json(p),null,"Missing/invalid expected value")); continue; }
                            float v=mat.GetFloat(p.name); actual=Number(v); pass=Finite(v)&&Math.Abs(v-p.value.Value)<=p.tolerance;
                        }
                        else
                        {
                            var c=p.color;
                            if(c==null||!Finite(c.r)||!Finite(c.g)||!Finite(c.b)||!Finite(c.a)) { detail.Add(C("materials.property","Unknown",target,Json(p),null,"Missing/invalid RGBA")); continue; }
                            var v=mat.GetColor(p.name); actual=Json(v);
                            pass=Finite(v.r)&&Finite(v.g)&&Finite(v.b)&&Finite(v.a)&&Math.Abs(v.r-c.r)<=p.tolerance&&Math.Abs(v.g-c.g)<=p.tolerance&&Math.Abs(v.b-c.b)<=p.tolerance&&Math.Abs(v.a-c.a)<=p.tolerance;
                        }
                        detail.Add(C("materials.property",pass?"Pass":"Fail",target,Json(p),actual,"Material name ignored; compares declared numeric meaning only"));
                    }
                }
                foreach(var r in root.GetComponentsInChildren<MeshRenderer>(true))
                {
                    string path=Relative(root.transform,r.transform);
                    var mf=r.GetComponent<MeshFilter>();
                    if(mf==null||mf.sharedMesh==null||mf.sharedMesh.subMeshCount!=r.sharedMaterials.Length)
                        detail.Add(C("materials.coverage","Unknown",path,"one mapped material per submesh",r.sharedMaterials.Length.ToString(),"Unsupported submesh/slot count mismatch"));
                    for(int i=0;i<r.sharedMaterials.Length;i++) if(!covered.Contains(path+"#"+i))
                        detail.Add(C("materials.coverage","Unknown",path+"#"+i,"explicit slot requirement",null,"Unmapped actual slot"));
                }
            }
            checks.Add(C("materials",Status(detail),"complete Renderer/slot/property mapping",m==null?null:Json(m),null,"See materials.* checks"));
            checks.AddRange(detail);
        }
        public static Report Evaluate(string requirementsPath)
        {
            var report=new Report {unityVersion=Application.unityVersion,colorSpace=PlayerSettings.colorSpace.ToString()};
            var checks=new List<Check>();
            try
            {
                var package=UnityEditor.PackageManager.PackageInfo.GetAllRegisteredPackages().FirstOrDefault(p=>p.name=="com.unity.render-pipelines.universal");
                report.urpVersion=package==null?null:package.version;
                checks.Add(C("environment",Application.unityVersion=="6000.5.10f1" && report.urpVersion=="17.5.0"?"Pass":"Unsupported","Editor/packages","Unity 6000.5.10f1; URP 17.5.0",report.unityVersion+"; "+report.urpVersion));
                if(!Path.IsPathRooted(requirementsPath)||!File.Exists(requirementsPath)) throw new SerializationException("Requirements must be an existing absolute JSON path");
                report.requirementsSha256=FileHash(requirementsPath);
                Requirements req;
                using(var stream=File.OpenRead(requirementsPath)) req=(Requirements)new DataContractJsonSerializer(typeof(Requirements)).ReadObject(stream);
                if(req==null || req.schemaVersion!=1) throw new SerializationException("Expected requirements schemaVersion 1");
                report.assetPath=req.assetPath;
                if(string.IsNullOrEmpty(req.assetPath)||!req.assetPath.StartsWith("Assets/",StringComparison.Ordinal)||req.assetPath.Contains('\\')||req.assetPath.Split('/').Any(p=>p==""||p=="."||p==".."))
                    throw new SerializationException("assetPath must be canonical Assets-relative path");
                if(!new[]{".fbx",".prefab"}.Contains(Path.GetExtension(req.assetPath).ToLowerInvariant()))
                    throw new SerializationException("Only static FBX/Prefab supported");
                var root=AssetDatabase.LoadAssetAtPath<GameObject>(req.assetPath);
                if(root==null) { checks.Add(C("identity","Fail",req.assetPath,req.dependencyFingerprint,null,"Target not found/imported")); }
                else
                {
                    string fingerprint=Fingerprint(req.assetPath);
                    bool match=req.dependencyFingerprint!=null && req.dependencyFingerprint.Length==64 && req.dependencyFingerprint==fingerprint;
                    checks.Add(C("identity",match?"Pass":"Fail",req.assetPath,req.dependencyFingerprint,fingerprint,"SHA256 of Assets dependencies and meta bytes; stale identity blocks further comparison"));
                    if(match && checks[0].status=="Pass")
                    {
                        // Static hierarchy only: no gameplay scripts or animation evaluation.
                        if(root.GetComponentsInChildren<Component>(true).Any(c=>c==null||(!(c is Transform)&&!(c is MeshRenderer)&&!(c is MeshFilter))))
                            checks.Add(C("assetType","Unsupported",req.assetPath,"Transform/MeshFilter/MeshRenderer only",null,"Nonstatic/other component in hierarchy"));
                        else
                        {
                            checks.Add(Size(root,req.dimensions));
                            checks.Add(Orientation(root,req.direction));
                            MaterialChecks(root,req.materials,checks);
                        }
                    }
                }
            }
            catch(Exception e) { checks.Add(C("input","Unknown",report.assetPath,"well-formed explicit supported requirements",null,e.GetType().Name+": "+e.Message)); }
            report.checks=checks.ToArray(); report.overall=Status(checks); return report;
        }
        static bool Within(string path,string directory)
        { return path.Equals(directory,StringComparison.OrdinalIgnoreCase)||path.StartsWith(directory.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase); }
        static void NoReparseAncestors(string path)
        {
            for(var d=new DirectoryInfo(path);d!=null;d=d.Parent)
                if(d.Exists && (d.Attributes&FileAttributes.ReparsePoint)!=0) throw new IOException("Report directory cannot traverse a junction/symlink");
        }
        public static Report RunFile(string requirementsPath,string outputDirectory,string reportName)
        {
            if(!Path.IsPathRooted(outputDirectory)) throw new IOException("Explicit absolute output directory required");
            string dir=Path.GetFullPath(outputDirectory);
            if(Within(dir,ProjectRoot)) throw new IOException("Reports must be outside the Unity project");
            NoReparseAncestors(dir);
            if(string.IsNullOrWhiteSpace(reportName)||reportName!=Path.GetFileName(reportName)||Path.GetExtension(reportName)!=".json"||reportName.IndexOfAny(Path.GetInvalidFileNameChars())>=0)
                throw new IOException("Report name must be a simple .json filename");
            string output=Path.Combine(dir,reportName);
            if(File.Exists(output)||string.Equals(Path.GetFullPath(requirementsPath),output,StringComparison.OrdinalIgnoreCase)) throw new IOException("Refusing to overwrite report/input");
            var report=Evaluate(requirementsPath);
            Directory.CreateDirectory(dir);
            using(var stream=new FileStream(output,FileMode.CreateNew,FileAccess.Write))
            using(var writer=new StreamWriter(stream,new UTF8Encoding(false))) writer.Write(JsonUtility.ToJson(report,true));
            return report;
        }
        public static void Run()
        {
            var args=Environment.GetCommandLineArgs();
            string Arg(string key) { int i=Array.IndexOf(args,key); if(i<0||i+1>=args.Length) throw new ArgumentException("Missing "+key); return args[i+1]; }
            var report=RunFile(Arg("-receiverRequirements"),Arg("-receiverOutputDir"),Arg("-receiverReportName"));
            Debug.Log("Asset receiver overall="+report.overall);
        }
    }
}
