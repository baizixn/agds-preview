"""Bounded editable SVG inspection, local edit, scope comparison and Edge export."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
DRAWABLE = {'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text'}
FORBIDDEN = {'script', 'foreignObject', 'image', 'animate', 'animateTransform', 'set'}
OUTPUT_WAIT_SECONDS = 5
OUTPUT_WAIT_INTERVAL_SECONDS = 0.05


def require(condition, message):
    if not condition:
        raise ValueError(message)


def absolute(value):
    p = Path(value)
    require(p.is_absolute(), 'Path must be absolute: ' + value)
    for ancestor in [p, *p.parents]:
        if ancestor.exists() or ancestor.is_symlink():
            st = ancestor.lstat()
            require(not ancestor.is_symlink() and not (getattr(st, 'st_file_attributes', 0) & 1024),
                    'Linked/reparse path refused: ' + str(ancestor))
    return p.resolve()


def inside(path, root):
    return path == root or root in path.parents


class Scope:
    def __init__(self, args):
        self.root = absolute(args.root)
        require(self.root.is_dir(), 'Explicit root must exist as a directory')
        self.allowed = [absolute(p) for p in args.allow]
        require(all(inside(p, self.root) for p in self.allowed), 'Allow entry escapes root')

    def path(self, value, source=False, output=False):
        p = absolute(value)
        require(inside(p, self.root), 'Path escapes explicit root: ' + str(p))
        require(any(p == a or (a.is_dir() and inside(p, a)) for a in self.allowed),
                'Path is outside explicit allowlist: ' + str(p))
        if source:
            require(p.is_file(), 'Input does not exist: ' + str(p))
        if output:
            require(not p.exists(), 'Output already exists; use a new revision: ' + str(p))
            require(p.parent.is_dir(), 'Output parent must already exist: ' + str(p.parent))
        return p


def digest(data):
    return hashlib.sha256(data).hexdigest()


def wait_for_stable_output(path, timeout=OUTPUT_WAIT_SECONDS, interval=OUTPUT_WAIT_INTERVAL_SECONDS):
    """Return a non-empty output only after its size and readable contents settle.

    Edge can report a successful subprocess exit before the screenshot becomes
    visible to the caller on Windows.  This bounded post-exit wait handles that
    handoff without weakening the existing PNG validation that follows.
    """
    deadline = time.monotonic() + timeout
    while True:
        try:
            first_size = path.stat().st_size
            if first_size > 0:
                time.sleep(interval)
                if path.stat().st_size == first_size:
                    with path.open('rb') as stream:
                        data = stream.read()
                    if len(data) == first_size and path.stat().st_size == first_size:
                        return data
        except OSError:
            pass
        if time.monotonic() >= deadline:
            raise ValueError('Edge produced no screenshot')
        time.sleep(interval)


def local(tag):
    return tag.rsplit('}', 1)[-1]


def read_svg(path):
    data = path.read_bytes()
    require(b'<!DOCTYPE' not in data.upper() and b'<!ENTITY' not in data.upper(), 'DTD/entities refused')
    root = ET.fromstring(data)
    require(root.tag == '{' + SVG + '}svg', 'Root must be SVG namespace svg')
    ids = {}
    groups, shapes = [], []
    for node in root.iter():
        tag = local(node.tag)
        require(tag not in FORBIDDEN, 'Unsupported non-static/vector element: ' + tag)
        node_id = node.get('id')
        if node_id is not None:
            require(bool(node_id.strip()), 'Empty ID refused')
            require(node_id not in ids, 'Duplicate ID: ' + node_id)
            ids[node_id] = node
        if tag == 'g':
            groups.append(node_id)
        if tag in DRAWABLE:
            shapes.append({'id': node_id, 'tag': tag})
        for key, value in node.attrib.items():
            require(not local(key).lower().startswith('on'), 'Event attributes refused')
            if local(key) == 'href':
                require(value.startswith('#'), 'External references refused')
        style_text = ' '.join(node.attrib.values()) + (node.text or '' if tag == 'style' else '')
        require('@import' not in style_text.lower(), 'CSS imports refused')
        for url in re.findall(r'url\s*\((.*?)\)', style_text, re.I | re.S):
            require(url.strip(' \t\r\n\"\'').startswith('#'), 'External URL refused')
    require(groups and shapes, 'Editable SVG requires actual groups and vector shapes/text')
    return root, ids, {'source_sha256': digest(data), 'groups': groups, 'shapes': shapes}


def canonical(node, excluded_id=None, excluded_attribute=None, text_context=False):
    """Attribute order/indentation independent; preserve text and child order.

    Text/tspan whitespace is meaningful and retained. Tail belongs to the parent
    scope, so excluding a subtree does not hide changes to its following text.
    """
    text_context = text_context or local(node.tag) in {'text', 'tspan', 'textPath'} or node.get('{http://www.w3.org/XML/1998/namespace}space') == 'preserve'
    norm = lambda value: value if value and (text_context or value.strip()) else ''
    tail = node.tail if node.tail and (text_context or node.tail.strip()) else ''
    if excluded_id is not None and node.get('id') == excluded_id and excluded_attribute is None:
        return ['EXCLUDED_SUBTREE', excluded_id, tail]
    attributes = dict(node.attrib)
    if excluded_id is not None and node.get('id') == excluded_id and excluded_attribute is not None:
        attributes.pop(excluded_attribute, None)
    return [node.tag, sorted(attributes.items()), norm(node.text), tail,
            [canonical(child, excluded_id, excluded_attribute, text_context) for child in node]]


def fingerprint(value):
    return digest(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def compare_roots(before, after, target, attribute=None):
    left = canonical(before, target, attribute)
    right = canonical(after, target, attribute)
    return {'outside_target_equal': left == right,
            'before_protected_sha256': fingerprint(left),
            'after_protected_sha256': fingerprint(right),
            'comparison': 'normalized XML excluding target subtree' if attribute is None else 'normalized XML excluding one target attribute'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'edit', 'compare', 'render'):
        sub = commands.add_parser(name)
        sub.add_argument('--root', required=True)
        sub.add_argument('--allow', action='append', required=True)
        sub.add_argument('--input', required=True)
        sub.add_argument('--dry-run', action='store_true')
        if name in ('edit', 'compare'):
            sub.add_argument('--id', required=True)
        if name == 'edit':
            sub.add_argument('--output', required=True)
            sub.add_argument('--attribute', required=True)
            sub.add_argument('--value', required=True)
        if name == 'compare':
            sub.add_argument('--other', required=True)
        if name == 'render':
            sub.add_argument('--output', required=True)
            sub.add_argument('--work-dir', required=True)
            sub.add_argument('--edge', required=True)
            sub.add_argument('--width', required=True, type=int)
            sub.add_argument('--height', required=True, type=int)
    args = parser.parse_args()
    scope = Scope(args)
    source = scope.path(args.input, source=True)
    output = scope.path(args.output, output=True) if hasattr(args, 'output') else None
    other = scope.path(args.other, source=True) if hasattr(args, 'other') else None
    root, ids, inventory = read_svg(source)
    report = {'command': args.command, 'input': str(source), 'dry_run': args.dry_run,
              'semantic_sha256': fingerprint(canonical(root)), **inventory}
    if args.command in ('edit', 'compare'):
        require(args.id in ids, 'Target ID not found: ' + args.id)
    if args.command == 'edit':
        require(args.attribute != 'id', 'Changing stable ID is not supported')
        require(args.attribute in ids[args.id].attrib, 'Target attribute does not exist')
        before = copy.deepcopy(root)
        old = ids[args.id].get(args.attribute)
        ids[args.id].set(args.attribute, args.value)
        payload = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        # Recheck static/vector constraints before any write, including dry-run.
        require(not local(args.attribute).lower().startswith('on') and local(args.attribute) != 'href', 'Executable/reference attribute edit refused')
        require('url(' not in args.value.lower() and '@import' not in args.value.lower(), 'Resource-bearing value edit refused')
        comparison = compare_roots(before, root, args.id, args.attribute)
        require(comparison['outside_target_equal'], 'Unexpected outside-attribute drift')
        report.update(output=str(output), target_id=args.id, attribute=args.attribute,
                      old_value=old, new_value=args.value, output_sha256=digest(payload), **comparison)
        if not args.dry_run:
            with output.open('xb') as stream:
                stream.write(payload)
            reopened, _, _ = read_svg(output)
            require(canonical(reopened) == canonical(root), 'Reopened output differs from intended XML')
            report['reopened_verified'] = True
    elif args.command == 'compare':
        after, after_ids, after_inventory = read_svg(other)
        require(args.id in after_ids, 'Target ID absent from other source: ' + args.id)
        comparison = compare_roots(root, after, args.id)
        report.update(other=str(other), other_sha256=after_inventory['source_sha256'], target_id=args.id, **comparison)
        report['target_changed'] = canonical(ids[args.id]) != canonical(after_ids[args.id])
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if comparison['outside_target_equal'] else 2
    elif args.command == 'render':
        work = scope.path(args.work_dir)
        require(work.is_dir(), 'Render work directory must already exist')
        edge = absolute(args.edge)
        require(edge.is_file(), 'Edge executable does not exist')
        require(args.width > 0 and args.height > 0, 'Viewport dimensions must be positive')
        require(output.suffix.lower() == '.png', 'Render output must be PNG')
        run_id = uuid.uuid4().hex
        profile = scope.path(str(work / ('edge-profile-' + run_id)), output=True)
        wrapper = scope.path(str(work / ('render-' + run_id + '.html')), output=True)
        root.set('width', str(args.width))
        root.set('height', str(args.height))
        html = '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;overflow:hidden}svg{display:block}</style>' + ET.tostring(root, encoding='unicode')
        command = [str(edge), '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
                   '--hide-scrollbars', '--force-device-scale-factor=1', '--run-all-compositor-stages-before-draw',
                   '--virtual-time-budget=1000', '--user-data-dir=' + str(profile),
                   '--window-size=' + str(args.width) + ',' + str(args.height),
                   '--screenshot=' + str(output), wrapper.as_uri()]
        report.update(output=str(output), profile=str(profile), wrapper=str(wrapper), viewport=[args.width, args.height], invocation=command)
        if not args.dry_run:
            profile.mkdir()
            with wrapper.open('x', encoding='utf-8') as stream:
                stream.write(html)
            run = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45,
                                 creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            report.update(exit_code=run.returncode, stdout=run.stdout, stderr=run.stderr)
            require(run.returncode == 0, 'Edge failed: ' + run.stderr)
            png = wait_for_stable_output(output)
            require(png[:8] == b'\x89PNG\r\n\x1a\n' and len(png) >= 24, 'Output is not a PNG')
            dimensions = list(struct.unpack('>II', png[16:24]))
            require(dimensions == [args.width, args.height], 'PNG dimensions differ from requested viewport: ' + str(dimensions))
            report.update(output_sha256=digest(png), png_dimensions=dimensions)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, ET.ParseError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'error': str(error), 'status': 'refused_or_failed'}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
