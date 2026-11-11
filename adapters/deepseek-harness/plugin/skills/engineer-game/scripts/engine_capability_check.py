import argparse, hashlib, html, json, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import Request, build_opener, HTTPRedirectHandler

HOSTS = {'docs.unity3d.com', 'docs.unity.com'}
LIMIT = 4 * 1024 * 1024

def digest(data): return hashlib.sha256(data).hexdigest()
def filehash(path): return digest(Path(path).read_bytes())
def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def resolve(base, path):
    p = Path(path)
    return p if p.is_absolute() else base / p

def inspect_project(root):
    root = Path(root).resolve()
    names = ['ProjectSettings/ProjectVersion.txt', 'Packages/manifest.json', 'Packages/packages-lock.json']
    files = {n: {'exists': (root/n).is_file(), 'sha256': filehash(root/n) if (root/n).is_file() else None} for n in names}
    if not files[names[0]]['exists'] or not files[names[1]]['exists']:
        raise ValueError('unsupported: 必须明确指定包含 Unity 版本与 manifest 的工程根目录')
    matches = re.findall(r'^m_EditorVersion:[ \t]*(\S+)[ \t]*$', (root/names[0]).read_text(encoding='utf-8-sig'), re.M)
    if len(matches) != 1 or not re.fullmatch(r'\d{4}\.\d+\.\d+[abfp]\d+(?:[a-zA-Z0-9.]*)?', matches[0]): raise ValueError('Unity 编辑器版本缺失、重复或格式无效')
    manifest = load(root/names[1]).get('dependencies', {})
    lock = load(root/names[2]).get('dependencies', {}) if files[names[2]]['exists'] else {}
    if not isinstance(manifest, dict) or not isinstance(lock, dict): raise ValueError('依赖格式无效')
    packages = {}
    for key in sorted(set(manifest) | set(lock)):
        item = lock.get(key, {})
        if not isinstance(item, dict): raise ValueError('锁文件依赖格式无效')
        packages[key] = {'declared': manifest.get(key), 'resolved': item.get('version'), 'source': item.get('source')}
    result = {'engine': 'Unity', 'engine_version': matches[0], 'root': str(root), 'files': files, 'packages': packages}
    result['fingerprint'] = digest(json.dumps(result, sort_keys=True, ensure_ascii=False).encode())
    return result

def scope(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in HOSTS or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('仅允许 HTTPS Unity 官方文档地址')
    path = unquote(parsed.path)
    package = re.search(r'/Packages/([^/@]+)@([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:[-.][A-Za-z0-9.-]+)?)(?:/|$)', path, re.I)
    if package: return {'kind': 'package', 'id': package.group(1), 'version': package.group(2)}
    engine = re.search(r'/(?:engine/)?(\d{4}\.\d+)(?:/|$)', path, re.I)
    if engine: return {'kind': 'engine', 'version': engine.group(1)}
    raise ValueError('官方地址必须包含明确版本，不能使用 current 或 latest')

class Redirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        scope(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.hidden=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden: self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def capture(url, directory, refresh=False):
    requested_scope = scope(url)
    directory = Path(directory).resolve(); directory.mkdir(parents=True, exist_ok=True)
    stem = digest(url.encode())
    meta = directory/(stem+'.json'); raw = directory/(stem+'.raw'); text = directory/(stem+'.txt')
    if meta.exists() and not refresh:
        info = validate_capture(meta)
        if info['requested_url'] == url: return meta
    response = build_opener(Redirect()).open(Request(url, headers={'User-Agent':'AGDS capability evidence/1'}), timeout=20)
    with response:
        final = response.geturl(); final_scope = scope(final)
        if final_scope != requested_scope: raise ValueError('重定向改变了文档版本范围')
        data = response.read(LIMIT+1)
        if len(data)>LIMIT: raise ValueError('文档超过 4 MiB 限制')
    parser=Text(); parser.feed(data.decode('utf-8', errors='replace'))
    readable=' '.join(' '.join(parser.parts).split()).encode('utf-8')
    raw.write_bytes(data); text.write_bytes(readable)
    save(meta, {'requested_url':url, 'final_url':final, 'sha256':digest(data), 'path':raw.name, 'text_path':text.name, 'text_sha256':digest(readable), 'version_scope':requested_scope})
    return meta

def validate_capture(path):
    path=Path(path); info=load(path)
    if scope(info['requested_url']) != info['version_scope'] or scope(info['final_url']) != info['version_scope']: raise ValueError('文档地址与版本范围不一致')
    if filehash(resolve(path.parent, info['path'])) != info['sha256'] or filehash(resolve(path.parent, info['text_path'])) != info['text_sha256']: raise ValueError('文档原始内容或文本已变化')
    return info

def check(record_path):
    record_path=Path(record_path).resolve(); base=record_path.parent; errors=[]
    def need(condition, message):
        if not condition: errors.append(message)
    try:
        r=load(record_path)
        if isinstance(r, dict) and r.get('kind') == 'engineering_plan':
            from engineering_plan_check import check_plan
            return check_plan(record_path)
        need(type(r.get('schema_version')) is int and r.get('schema_version') == 1, 'schema_version 必须为 1')
        inv_path=resolve(base,r['inventory']); inv=load(inv_path); current=inspect_project(inv['root'])
        need(inv == current, '工程清单已过期或被修改')
        task=r['task']; source=task['source']
        need(isinstance(task['id'], str) and bool(task['id'].strip()), '任务 ID 缺失')
        need(task['trigger'] in ('new_capability','replacement','uncertainty','routine_fix'), '任务触发类型无效')
        need(task['permission'] in ('inspect','probe','implementation'), '任务权限无效')
        need(filehash(resolve(base,source['path'])) == source['sha256'], '任务源文件已变化')
        existing=r['existing']; native=r['native']; decision=r['decision']; probe=r['probe']
        need(existing['status'] in ('found','none','unknown') and isinstance(existing['summary'],str) and bool(existing['summary'].strip()), '现有实现状态或说明无效')
        need(native['status'] in ('fits','partial','unsuitable','unknown','not_needed'), '原生能力状态无效')
        need(decision['path'] in ('existing','native','native_with_glue','custom','unresolved') and isinstance(decision['reason'],str) and bool(decision['reason'].strip()), '决策无效')
        need(isinstance(decision['gaps'],list) and all(isinstance(x,str) and x.strip() for x in decision['gaps']), '缺口必须是非空文本列表')
        need(isinstance(probe['required'],bool) and probe['result'] in ('not_required','not_run','pass','fail','inconclusive'), '探针状态无效')
        entries={}
        for e in r['evidence']:
            eid=e['id']; need(bool(eid) and eid not in entries, '证据 ID 缺失或重复'); entries[eid]=e
            need(e['kind'] in ('local','official','probe'), '证据类型无效')
            p=resolve(base,e['path']); need(filehash(p)==e['sha256'], '证据文件已变化: '+str(eid))
            if e['kind']=='official':
                info=validate_capture(p); s=info['version_scope']
                if s['kind']=='engine': matched=inv['engine_version'].startswith(s['version']+'.')
                else: matched=inv['packages'].get(s['id'],{}).get('resolved')==s['version']
                need(matched, '官方文档版本与工程不匹配: '+str(eid))
        def refs(obj, kind):
            ids=obj['evidence']; need(isinstance(ids,list), '证据引用必须是列表')
            for eid in ids: need(eid in entries and entries[eid]['kind']==kind, '证据引用缺失或类型错误: '+str(eid))
            return bool(ids)
        local=refs(existing,'local'); official=refs(native,'official'); proberef=refs(probe,'probe')
        need(existing['status'] in ('found','none') and local, '现有实现需要本地证据')
        path=decision['path']; ns=native['status']
        if path=='existing': need(existing['status']=='found', '复用已有实现需要 found 证据')
        else:
            need(official and isinstance(native['candidate'],str) and bool(native['candidate'].strip()) and isinstance(native['reason'],str) and bool(native['reason'].strip()), '需要明确原生候选、原因和匹配版本的官方证据')
            need((path=='native' and ns=='fits') or (path=='native_with_glue' and ns=='partial' and bool(decision['gaps'])) or (path=='custom' and ns=='unsuitable' and bool(decision['gaps'])), '原生状态和决策不匹配，未知或缺少缺口不能通过')
        if probe['result']=='pass':
            need(proberef, '通过的探针需要原始证据')
            for eid in probe['evidence']:
                if eid in entries and entries[eid]['kind']=='probe':
                    context=entries[eid].get('context', {})
                    need(isinstance(context,dict) and context.get('environment_fingerprint')==current['fingerprint'] and context.get('task_sha256')==source['sha256'], '探针与当前工程或任务不匹配')
        if probe['required']: need(probe['result']=='pass' and proberef, '必需探针需要通过并提供原始证据')
        else: need(probe['result'] in ('not_required','pass'), '探针结果尚未通过')
        return {'status':'blocked' if errors else 'evidence_ready', 'implementation_allowed':not errors and task['permission']=='implementation', 'reasons':errors, 'root':inv['root']}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as exc:
        return {'status':'blocked','implementation_allowed':False,'reasons':errors+['输入或证据无效: '+str(exc)],'root':None}

def main(argv=None):
    parser=argparse.ArgumentParser(description='Unity 能力证据检查；guard 只门控通过本工具运行的命令，不授予权限。')
    sub=parser.add_subparsers(dest='cmd', required=True)
    p=sub.add_parser('inspect'); p.add_argument('--root',required=True); p.add_argument('--output',required=True)
    p=sub.add_parser('capture'); p.add_argument('--url',required=True); p.add_argument('--directory',required=True); p.add_argument('--refresh',action='store_true')
    p=sub.add_parser('check'); p.add_argument('--record',required=True); p.add_argument('--output')
    p=sub.add_parser('guard'); p.add_argument('--record',required=True); p.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args(argv)
    try:
        if args.cmd=='inspect':
            inv=inspect_project(args.root); out=Path(args.output).resolve()
            if out in [(Path(inv['root'])/n).resolve() for n in inv['files']]: raise ValueError('输出不能覆盖工程输入')
            if out.exists():
                try: old=load(out)
                except (ValueError,OSError): raise ValueError('输出已存在且不是工程清单')
                if not isinstance(old,dict) or old.get('engine')!='Unity' or old.get('root')!=inv['root'] or not all(k in old for k in ('files','packages','fingerprint','engine_version')): raise ValueError('输出已存在且不是同一工程清单')
            save(out,inv); print(out); return 0
        if args.cmd=='capture': print(capture(args.url,args.directory,args.refresh)); return 0
        result=check(args.record)
        if args.cmd=='check':
            if args.output:
                out=Path(args.output).resolve(); r=load(args.record); protected=[Path(args.record).resolve(),resolve(Path(args.record).resolve().parent,r['inventory']).resolve(),resolve(Path(args.record).resolve().parent,r['task']['source']['path']).resolve()]
                protected += [resolve(Path(args.record).resolve().parent,e['path']).resolve() for e in r['evidence']]
                for e in r['evidence']:
                    if e['kind']=='official':
                        meta=resolve(Path(args.record).resolve().parent,e['path']); info=load(meta)
                        protected += [resolve(meta.parent,info[k]).resolve() for k in ('path','text_path')]
                if result['root']: protected += [(Path(result['root'])/n).resolve() for n in ('ProjectSettings/ProjectVersion.txt','Packages/manifest.json','Packages/packages-lock.json')]
                if out in protected: raise ValueError('输出不能覆盖输入证据')
                save(out,result)
            print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['status']=='evidence_ready' else 1
        command=args.command
        if command and command[0]=='--': command=command[1:]
        if not result['implementation_allowed'] or not command:
            print(json.dumps(result,ensure_ascii=False),file=sys.stderr); return 1
        return subprocess.run(command,cwd=result['root'],shell=False).returncode
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print('错误: '+str(exc),file=sys.stderr); return 1
if __name__=='__main__': sys.exit(main())
