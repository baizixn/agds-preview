#!/usr/bin/env python3
"""Prepare a local feedback packet; never send it or inspect project context."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlencode, urlsplit, urlunsplit


FIELDS = ("title", "context", "observed", "expected", "version", "reproduction")
URL_LIMIT = 1800


def repository_url(value):
    if not value or any(char.isspace() for char in value):
        raise ValueError("Repository URL must be a non-empty HTTP(S) URL without whitespace")
    parsed = urlsplit(value)
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment):
        raise ValueError("Use a repository URL without credentials, query or fragment")
    _ = parsed.port  # Validate malformed/out-of-range ports without connecting.
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.lstrip("/").split("/")
    if (len(parts) < 2 or any(part in (".", "..") or not re.fullmatch(r"[A-Za-z0-9_.~-]+", part)
                              for part in parts)):
        raise ValueError("Repository URL must include an owner and repository path")
    return urlunsplit((parsed.scheme, parsed.netloc, "/" + "/".join(parts), "", ""))


def build_packet(data, repo_url=None):
    if not isinstance(data, dict) or set(data) - set(FIELDS):
        raise ValueError("Input must be an object containing only documented feedback fields")
    if any(not isinstance(value, str) for value in data.values()):
        raise ValueError("Feedback fields must be strings; omit unknown fields")
    data = {key: value.strip() for key, value in data.items()}
    if not data.get("observed"):
        raise ValueError("observed must describe an actual problem or suggestion")
    title = data.get("title") or "AGDS 反馈：" + data["observed"].splitlines()[0][:70]
    if len(title) > 200 or "\n" in title or "\r" in title:
        raise ValueError("title must be one line of at most 200 characters")
    labels = (("context", "想完成的任务"), ("observed", "实际情况"),
              ("expected", "期望结果"), ("version", "使用版本"),
              ("reproduction", "最小复现或证据"))
    body = "\n\n".join("## " + label + "\n\n" + (data.get(key) or "未确认")
                       for key, label in labels)
    body += "\n\n这是使用反馈；提交不代表已复现、已批准共享修改或已发布升级。\n"
    destination = repository_url(repo_url) if repo_url is not None else None
    url = None
    mode = "file_only"
    if destination:
        form_url = destination + "/issues/new"
        prefilled = form_url + "?" + urlencode({"title": title, "body": body}, quote_via=quote)
        mode = "prefilled_url" if len(prefilled) <= URL_LIMIT else "form_and_file"
        url = prefilled if mode == "prefilled_url" else form_url
    identity = json.dumps({"destination": destination, "title": title, "body": body},
                          ensure_ascii=False, sort_keys=True).encode("utf-8")
    packet = {"schema_version": 1, "status": "prepared", "transport": "none",
              "draft_sha256": hashlib.sha256(identity).hexdigest(),
              "destination": destination, "title": title, "body": body,
              "mode": mode, "issue_url": url}
    markdown = "# " + title + "\n\n尚未提交。" + ("\n\n反馈仓库：" + destination if destination else "")
    markdown += "\n\n" + body
    files = {"feedback.md": markdown.encode("utf-8"),
             "packet.json": (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}
    if url:
        files["issue-url.txt"] = (url + "\n").encode("utf-8")
    return packet, files


def prepare(data, output_dir, repo_url=None):
    packet, files = build_packet(data, repo_url)
    target = Path(output_dir)
    if target.exists() or target.is_symlink():
        if target.is_symlink() or not target.is_dir():
            raise ValueError("Output must be a new directory or an identical previous packet")
        if (set(item.name for item in target.iterdir()) != set(files)
                or any((target / name).is_symlink() or not (target / name).is_file()
                       or (target / name).read_bytes() != content for name, content in files.items())):
            raise ValueError("Output already exists with different/incomplete content; nothing overwritten")
    else:
        target.mkdir(parents=True, exist_ok=False)
        for name, content in files.items():
            with (target / name).open("xb") as stream:
                stream.write(content)
    return {"status": packet["status"], "mode": packet["mode"],
            "draft_sha256": packet["draft_sha256"],
            "packet_path": str((target / "packet.json").resolve()),
            "feedback_path": str((target / "feedback.md").resolve())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Curated UTF-8 JSON, not raw project logs")
    parser.add_argument("--output-dir", required=True, type=Path, help="New task-local feedback directory")
    parser.add_argument("--repo-url", help="Confirmed AGDS repository URL on GitHub; omit for file only")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        print(json.dumps(prepare(data, args.output_dir, args.repo_url), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        print("Feedback preparation failed: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
