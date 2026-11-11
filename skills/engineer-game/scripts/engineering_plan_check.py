"""Mechanical evidence and completeness checks for a bounded engineering plan."""
from pathlib import Path
from urllib.parse import urlparse

from engine_capability_check import filehash, inspect_project, load, resolve


def check_plan(record_path):
    base = Path(record_path).resolve().parent
    errors = []
    root = None

    def need(condition, message):
        if not condition:
            errors.append(message)

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def texts(value, required=True):
        return isinstance(value, list) and (bool(value) or not required) and all(text(x) for x in value)

    try:
        r = load(record_path)
        need(type(r.get('schema_version')) is int and r['schema_version'] == 1, 'schema_version 必须为 1')
        inv = load(resolve(base, r['inventory']))
        current = inspect_project(inv['root'])
        root = inv['root']
        need(inv == current, '工程清单已过期或被修改')
        task = r['task']
        source = task['source']
        need(text(task['id']) and task['level'] in ('project', 'module'), '任务 ID 或级别无效')
        need(task['permission'] in ('inspect', 'probe', 'implementation'), '任务权限无效')
        need(filehash(resolve(base, source['path'])) == source['sha256'], '任务源文件已变化')
        entries = {}
        for e in r['evidence']:
            eid = e['id']
            need(text(eid) and eid not in entries, '证据 ID 缺失或重复')
            entries[eid] = e
            need(e['kind'] in ('local', 'primary', 'measurement'), '证据类型无效')
            need(filehash(resolve(base, e['path'])) == e['sha256'], '证据文件已变化: ' + str(eid))
            if e['kind'] == 'primary':
                url = urlparse(e['url'])
                need(url.scheme == 'https' and bool(url.netloc) and text(e['issuer']) and text(e['version']), '来源声明不完整')
            if e['kind'] == 'measurement':
                context = e['context']
                need(context['environment_fingerprint'] == current['fingerprint'] and context['task_sha256'] == source['sha256'], '测量上下文已变化')
        need(any(e.get('kind') == 'primary' for e in entries.values()), '引擎与 GC 配置需要版本来源声明')

        def refs(ids, kind=None, required=False):
            valid = isinstance(ids, list) and (bool(ids) or not required)
            if valid:
                valid = all(x in entries and (kind is None or entries[x]['kind'] == kind) for x in ids)
            need(valid, '证据引用缺失或类型错误')
            return valid and bool(ids)

        framework = r['framework']
        refs(framework['existing_evidence'], 'local', True)
        candidates = {}
        for c in framework['candidates']:
            cid = c['id']
            need(text(cid) and cid not in candidates, '候选 ID 缺失或重复')
            candidates[cid] = c
            need(c['origin'] in ('existing', 'engine', 'first_party', 'third_party', 'custom'), '候选来源无效')
            need(c['fit'] in ('fits', 'partial', 'unsuitable', 'unknown') and text(c['reason']), '候选适配说明无效')
            need(c['maintenance'] in ('current', 'stale', 'unknown') and c['license'] in ('compatible', 'incompatible', 'unknown'), '维护或许可状态无效')
            refs(c['evidence'], required=True)
            if c['origin'] not in ('existing', 'custom'):
                need(any(entries.get(x, {}).get('kind') == 'primary' for x in c['evidence']), '候选缺少主要来源')
        selection = framework['selection']
        chosen = candidates[selection['id']]
        strategy = selection['strategy']
        need(strategy in ('reuse', 'configure', 'extend', 'adapter', 'fork', 'custom') and text(selection['reason']), '选择说明无效')
        need(texts(selection['gaps'], False), '缺口格式无效')
        need(type(selection['dependency_change']) is bool, '依赖变更状态无效')
        refs(selection['change_authority_evidence'], required=strategy == 'fork' or selection['dependency_change'] is True)
        if chosen['origin'] != 'custom':
            need(strategy != 'custom', '自研策略需要自研候选')
            need(text(chosen['version']) and chosen['version'].strip().lower() != 'unknown' and chosen['fit'] in ('fits', 'partial') and chosen['license'] == 'compatible', '选中候选版本、适配或许可不明确')
            if chosen['origin'] == 'third_party':
                need(chosen['maintenance'] == 'current', '第三方候选维护状态不明确')
        else:
            need(strategy == 'custom' and texts(selection['gaps']) and any(c['origin'] != 'custom' and c['fit'] == 'unsuitable' and c['evidence'] for c in candidates.values()), '自研缺少有证据的对比或具体缺口')
        memory = r['memory']
        for key in ('engine_profile', 'ownership', 'measurement_plan'):
            need(text(memory[key]), '内存计划缺少 ' + key)
        for key in ('hot_paths', 'allocation_lifetimes', 'peak_strategy', 'retention_limits', 'release_paths'):
            need(texts(memory[key]), '内存计划缺少 ' + key)
        need(memory['budget_status'] in ('unknown', 'defined') and isinstance(memory['budgets'], dict), '预算状态无效')
        validation = memory['validation']
        state = validation['state']
        need(state in ('not_run', 'pass', 'fail', 'inconclusive'), '验证状态无效')
        measured = refs(validation['evidence'], 'measurement', state == 'pass')
        if state == 'pass':
            need(measured and all(text(validation[k]) for k in ('artifact_id', 'environment', 'scenario')) and isinstance(validation['metrics'], dict) and bool(validation['metrics']) and memory['budget_status'] == 'defined' and bool(memory['budgets']), '性能通过缺少预算、测量或上下文')
        return {'status': 'blocked' if errors else 'evidence_ready', 'implementation_allowed': not errors and task['permission'] == 'implementation', 'performance_verified': False, 'performance_evidence_ready': not errors and state == 'pass', 'declared_performance_state': state, 'reasons': errors, 'root': root}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return {'status': 'blocked', 'implementation_allowed': False, 'performance_verified': False, 'performance_evidence_ready': False, 'declared_performance_state': None, 'reasons': errors + ['输入或证据无效: ' + str(exc)], 'root': root}
