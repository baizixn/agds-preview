"""Read-only presence/identity check; does not approve or execute scene changes."""
import argparse
import hashlib
import json
from pathlib import Path


def check(record_path, writer):
    path = Path(record_path).resolve()
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            return {"status": "pending", "missing": ["record_object"]}
        missing = [key for key in ("decision_owner", "writer", "specification")
                   if not isinstance(record.get(key), str) or not record[key].strip()]
        if missing:
            return {"status": "pending", "missing": missing}
        if record["writer"] != writer:
            return {"status": "pending", "missing": ["assigned_writer_match"]}
        specification = (path.parent / record["specification"]).resolve()
        if not specification.is_file():
            return {"status": "pending", "missing": ["specification_file"]}
        digest = hashlib.sha256(specification.read_bytes()).hexdigest()
        return {"status": "ready", "decision_owner": record["decision_owner"],
                "writer": writer, "specification_path": str(specification),
                "specification_sha256": digest}
    except (OSError, ValueError) as error:
        return {"status": "pending", "missing": ["readable_record_or_specification"],
                "error": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True)
    parser.add_argument("--writer", required=True)
    args = parser.parse_args()
    result = check(args.record, args.writer)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
