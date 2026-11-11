import argparse, copy, hashlib, html, json, re, secrets, sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

class PanelError(ValueError): pass

def require(ok, message):
    if not ok: raise PanelError(message)

def string(obj, key, where, empty=False):
    require(isinstance(obj, dict) and isinstance(obj.get(key), str) and (empty or bool(obj[key].strip())), f'{where}.{key}: 必须是文本')
    return obj[key]

def array(obj, key, where):
    v = obj.get(key) if isinstance(obj, dict) else None
    require(isinstance(v, list), f'{where}.{key}: 必须是数组')
    require(all(isinstance(x, str) and x.strip() for x in v), f'{where}.{key}: 数组项必须是非空文本')
    return v

def choice(obj, key, choices, where):
    v = string(obj, key, where); require(v in choices, f'{where}.{key}: 无效值 {v}'); return v

def load_panel(input_path):
    path = Path(input_path).resolve()
    try: data = json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as e: raise PanelError(f'输入读取失败: {e}') from e
    require(isinstance(data, dict) and type(data.get('schema_version')) is int and data['schema_version'] == 1, 'schema_version: 必须为 1')
    string(data, 'project', '根'); updated = string(data, 'updated_at', '根')
    try: datetime.fromisoformat(updated.replace('Z', '+00:00'))
    except ValueError: raise PanelError('updated_at: 必须是 ISO 日期时间')
    src = data.get('source'); sp = string(src, 'path', 'source'); digest = string(src, 'sha256', 'source'); string(src, 'label', 'source')
    require(Path(sp).is_absolute(), 'source.path: 必须是绝对路径')
    require(bool(re.fullmatch(r'[0-9a-fA-F]{64}', digest)), 'source.sha256: 格式错误')
    try: actual = hashlib.sha256(Path(sp).read_bytes()).hexdigest()
    except OSError as e: raise PanelError(f'来源文件缺失或无法读取: {e}') from e
    require(actual.lower() == digest.lower(), '来源摘要不匹配，台账可能已更新')
    d = data.get('delivery'); choice(d, 'kind', {'partial_test','progress','stage_review'}, 'delivery'); string(d,'summary','delivery')
    for k in ('test_scope','not_ready','expected'): array(d,k,'delivery')
    if 'stage_ids' in d: array(d,'stage_ids','delivery')
    require(d['kind'] != 'partial_test' or (d.get('stage_ids') and d['test_scope']), 'partial_test: 必须指定关联阶段及测试范围')
    stages = data.get('stages'); require(isinstance(stages,list) and stages, 'stages: 必须是非空数组')
    ids=set(); itemids=set()
    for s in stages:
        sid=string(s,'id','stage'); require(sid not in ids, f'阶段 ID 重复: {sid}'); ids.add(sid)
        for k in ('title','goal','artifact_revision','exit'): string(s,k,sid)
        for k in ('dependencies','conditions','tests'): array(s,k,sid)
        state=choice(s,'scope_state',{'candidate','approved'},sid); ev=string(s,'scope_evidence',sid,True)
        require(state != 'approved' or ev.strip(), f'{sid}: 已批准范围缺少来源')
        choice(s,'execution',{'planned','active','paused'},sid)
        owner=s.get('owner_acceptance'); choice(owner,'state',{'pending','accepted','rejected'},sid+'.owner_acceptance'); string(owner,'evidence',sid+'.owner_acceptance',True)
        items=s.get('items'); require(isinstance(items,list), f'{sid}.items: 必须是数组')
        for i in items:
            iid=string(i,'id',sid); require(iid not in itemids, f'条目 ID 重复: {iid}'); itemids.add(iid)
            for k in ('title','source_ref'): string(i,k,iid)
            choice(i,'scope',{'Must','Should','Could','Deferred'},iid)
            imp=i.get('implementation'); ver=i.get('verification')
            choice(imp,'state',{'unknown','todo','in_progress','done','blocked'},iid+'.implementation')
            choice(ver,'state',{'unknown','not_run','pass','fail','stale','inconclusive'},iid+'.verification')
            for obj, keys, name in ((imp,('evidence','revision'),'implementation'),(ver,('evidence','revision','environment'),'verification')):
                for k in keys: string(obj,k,iid+'.'+name,True)
    require(all(x in ids for x in d.get('stage_ids', [])), 'delivery.stage_ids: 关联阶段不存在')
    require(Path(sp).resolve() != path, 'source.path 不能与输入相同')
    for s in stages:
        require(all(x in ids for x in s['dependencies']), f"{s['id']}: 依赖阶段不存在")
    for s in summarize(data)['stages']:
        orig=next(x for x in stages if x['id']==s['id']); owner=orig['owner_acceptance']
        require(owner['state'] != 'accepted' or (owner['evidence'].strip() and s['ready']), f"{s['id']}: Owner 验收缺少来源或阶段未达到待验收条件")
    return data

def effective(s,i):
    imp=i['implementation']; ver=i['verification']; rev=s['artifact_revision']
    valid_rev=bool(rev.strip()) and rev.lower()!='unknown'
    impl=imp['state']
    if impl=='done' and not (imp['evidence'].strip() and valid_rev and imp['revision']==rev): impl='unknown'
    test=ver['state']
    if test=='pass' and not (impl=='done' and ver['evidence'].strip() and ver['environment'].strip() and valid_rev and ver['revision']==rev): test='stale' if ver['revision'] and valid_rev and ver['revision']!=rev else 'unknown'
    return impl,test

def summarize(panel):
    out=[]
    for s in panel['stages']:
        must=[i for i in s['items'] if i['scope']=='Must']; states=[effective(s,i) for i in must]
        implemented=sum(a=='done' for a,b in states); verified=sum(b=='pass' for a,b in states)
        ready=bool(must) and s['scope_state']=='approved' and bool(s['scope_evidence'].strip()) and implemented==len(must) and verified==len(must)
        out.append(dict(id=s['id'],total=len(must),implemented=implemented,verified=verified,unknown=sum(a=='unknown' or b=='unknown' for a,b in states),ready=ready,label=('已验收' if s['owner_acceptance']['state']=='accepted' else '验收需处理' if s['owner_acceptance']['state']=='rejected' else '待 Owner 验收' if ready else ('无必需项' if not must else '未核实' if all(a=='unknown' and b in ('unknown','not_run') for a,b in states) else {'planned':'计划中','active':'进行中','paused':'已暂停'}[s['execution']]))))
    return {'stages':out}

build_summary=summarize

def render(panel, live=False):
    template=(Path(__file__).resolve().parent.parent/'assets'/'stage-panel.html').read_text(encoding='utf-8')
    payload=json.dumps({'panel':panel,'summary':summarize(panel),'live':live},ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return template.replace('/*PANEL_DATA*/',payload)

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    for name in ('validate','render','serve'):
        a=sub.add_parser(name); a.add_argument('--input',required=True)
        if name=='render': a.add_argument('--output',required=True)
        if name=='serve': a.add_argument('--port',type=int,default=0)
    a=p.parse_args(); panel=load_panel(a.input)
    if a.cmd=='validate': print(json.dumps(summarize(panel),ensure_ascii=False)); return
    if a.cmd=='render':
        out=Path(a.output).resolve(); require(out != Path(a.input).resolve() and out != Path(panel['source']['path']).resolve(), '输出不能覆盖输入或原始来源')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(panel),encoding='utf-8'); return
    token=secrets.token_urlsafe(32); route='/'+token
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self): self.reply(False)
        def do_GET(self): self.reply(True)
        def reply(self, body):
            host=self.headers.get('Host','')
            if host not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}') or urlsplit(self.path).path != route or urlsplit(self.path).query:
                self.send_error(404); return
            try: content=render(load_panel(a.input),True).encode('utf-8'); status=200
            except (PanelError,OSError,ValueError) as e: content=('数据读取失败：'+str(e)).encode('utf-8'); status=503
            self.send_response(status); self.send_header('Content-Type','text/html; charset=utf-8' if status==200 else 'text/plain; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(content))); self.end_headers()
            if body: self.wfile.write(content)
        def log_message(self,*args): pass
    server=HTTPServer(('127.0.0.1',a.port),Handler); print(json.dumps({'url':f'http://127.0.0.1:{server.server_port}{route}'}),flush=True); server.serve_forever()
if __name__=='__main__':
    try: main()
    except (PanelError,OSError,ValueError) as e: print(str(e),file=sys.stderr); sys.exit(1)
