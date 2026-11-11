from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any


class RecordValidationError(ValueError):
    def __init__(self, message: str, line: int | None = None) -> None:
        self.message = message
        self.line = line
        super().__init__(message)


@dataclass(frozen=True)
class LogicalLine:
    number: int
    indent: int
    content: str


def strip_yaml_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    index = 0
    while index < len(value):
        char = value[index]
        if quote == '"':
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = None
        elif quote == "'":
            if char == "'" and index + 1 < len(value) and value[index + 1] == "'":
                index += 1
            elif char == "'":
                quote = None
        elif char in {'"', "'"} and (
            index == 0 or value[index - 1].isspace() or value[index - 1] in ":,[{"
        ):
            quote = char
        elif char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
        index += 1
    if quote is not None:
        raise RecordValidationError("unterminated quoted scalar")
    return value.rstrip()


def split_mapping_entry(content: str) -> tuple[str, str] | None:
    quote: str | None = None
    escaped = False
    index = 0
    while index < len(content):
        char = content[index]
        if quote == '"':
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = None
        elif quote == "'":
            if char == "'" and index + 1 < len(content) and content[index + 1] == "'":
                index += 1
            elif char == "'":
                quote = None
        elif char in {'"', "'"} and (
            index == 0
            or content[index - 1].isspace()
            or content[index - 1] in ":,[{"
        ):
            quote = char
        elif char == ":" and (
            index + 1 == len(content) or content[index + 1].isspace()
        ):
            return content[:index].strip(), content[index + 1 :].strip()
        index += 1
    return None


def parse_json_without_duplicate_keys(text: str) -> Any:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise RecordValidationError(f"duplicate mapping key: {key}")
            result[key] = value
        return result

    try:
        return json.loads(text, object_pairs_hook=pairs_hook)
    except RecordValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise RecordValidationError(f"malformed JSON: {exc.msg}", exc.lineno) from exc


class YamlSubsetParser:
    BLOCK_SCALAR = re.compile(r"^[>|](?:[+-]?[1-9]?|[1-9][+-]?)$")
    PLAIN_KEY = re.compile(r"^[A-Za-z0-9_.-]+$")
    INTEGER = re.compile(r"^[+-]?(?:0|[1-9][0-9]*)$")
    FLOAT = re.compile(
        r"^[+-]?(?:(?:0|[1-9][0-9]*)\.[0-9]+|(?:0|[1-9][0-9]*)[eE][+-]?[0-9]+)$"
    )

    def __init__(self, text: str) -> None:
        self.lines = self._logical_lines(text)
        self.position = 0

    def _logical_lines(self, text: str) -> list[LogicalLine]:
        lines: list[LogicalLine] = []
        for number, raw in enumerate(text.splitlines(), start=1):
            if "\t" in raw[: len(raw) - len(raw.lstrip(" \t"))]:
                raise RecordValidationError("tab indentation is outside the supported YAML subset", number)
            stripped = raw.lstrip(" ")
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(raw) - len(stripped)
            try:
                content = strip_yaml_comment(stripped)
            except RecordValidationError as exc:
                raise RecordValidationError(exc.message, number) from exc
            if not content:
                continue
            if content in {"---", "..."}:
                if lines:
                    raise RecordValidationError(
                        "multiple documents are outside the supported YAML subset", number
                    )
                continue
            lines.append(LogicalLine(number, indent, content))
        return lines

    def parse(self) -> Any:
        if not self.lines:
            return None
        if self.lines[0].indent != 0:
            raise RecordValidationError("top-level content must start at indentation 0", self.lines[0].number)
        result = self._parse_block(0)
        if self.position != len(self.lines):
            line = self.lines[self.position]
            raise RecordValidationError("unexpected trailing YAML content", line.number)
        return result

    def _parse_block(self, indent: int) -> Any:
        line = self.lines[self.position]
        if line.indent != indent:
            raise RecordValidationError("inconsistent indentation", line.number)
        if line.content == "-" or line.content.startswith("- "):
            return self._parse_sequence(indent)
        return self._parse_mapping(indent)

    def _parse_mapping(
        self,
        indent: int,
        initial: dict[str, Any] | None = None,
        key_lines: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        result = initial if initial is not None else {}
        seen = key_lines if key_lines is not None else {}
        while self.position < len(self.lines):
            line = self.lines[self.position]
            if line.indent < indent:
                break
            if line.indent > indent:
                raise RecordValidationError("unexpected mapping indentation", line.number)
            if line.content == "-" or line.content.startswith("- "):
                break
            key, raw_value = self._mapping_pair(line.content, line.number)
            if key in seen:
                raise RecordValidationError(
                    f"duplicate mapping key: {key} (first declared on line {seen[key]})",
                    line.number,
                )
            seen[key] = line.number
            self.position += 1
            result[key] = self._consume_value(raw_value, indent, line.number)
        return result

    def _parse_sequence(self, indent: int) -> list[Any]:
        result: list[Any] = []
        while self.position < len(self.lines):
            line = self.lines[self.position]
            if line.indent < indent:
                break
            if line.indent > indent:
                raise RecordValidationError("unexpected sequence indentation", line.number)
            if not (line.content == "-" or line.content.startswith("- ")):
                break
            rest = line.content[1:].strip()
            self.position += 1
            if not rest:
                if self.position < len(self.lines) and self.lines[self.position].indent > indent:
                    result.append(self._parse_block(self.lines[self.position].indent))
                else:
                    result.append(None)
                continue

            pair = split_mapping_entry(rest)
            if pair is None:
                result.append(self._parse_scalar(rest, line.number))
                if self.position < len(self.lines) and self.lines[self.position].indent > indent:
                    raise RecordValidationError(
                        "a scalar sequence item cannot own an indented block",
                        self.lines[self.position].number,
                    )
                continue

            mapping_indent = indent + 2
            key, raw_value = self._mapping_pair(rest, line.number)
            item: dict[str, Any] = {}
            seen = {key: line.number}
            item[key] = self._consume_value(raw_value, mapping_indent, line.number)
            if self.position < len(self.lines) and self.lines[self.position].indent > indent:
                next_line = self.lines[self.position]
                if next_line.indent != mapping_indent:
                    raise RecordValidationError(
                        "sequence mapping entries must use two-space continuation indentation",
                        next_line.number,
                    )
                self._parse_mapping(mapping_indent, item, seen)
            result.append(item)
        return result

    def _mapping_pair(self, content: str, line_number: int) -> tuple[str, str]:
        pair = split_mapping_entry(content)
        if pair is None:
            raise RecordValidationError("expected a mapping entry", line_number)
        raw_key, raw_value = pair
        if not raw_key:
            raise RecordValidationError("mapping key cannot be empty", line_number)
        if raw_key[0:1] in {'"', "'"}:
            key = self._parse_scalar(raw_key, line_number)
            if not isinstance(key, str):
                raise RecordValidationError("mapping key must be a string", line_number)
        elif self.PLAIN_KEY.fullmatch(raw_key):
            key = raw_key
        else:
            raise RecordValidationError(
                "mapping key is outside the supported YAML subset", line_number
            )
        return key, raw_value

    def _consume_value(self, raw_value: str, parent_indent: int, line_number: int) -> Any:
        if self.BLOCK_SCALAR.fullmatch(raw_value):
            content: list[str] = []
            while (
                self.position < len(self.lines)
                and self.lines[self.position].indent > parent_indent
            ):
                content.append(self.lines[self.position].content)
                self.position += 1
            separator = "\n" if raw_value.startswith("|") else " "
            return separator.join(content)
        if not raw_value:
            if self.position < len(self.lines) and self.lines[self.position].indent > parent_indent:
                return self._parse_block(self.lines[self.position].indent)
            return None
        value = self._parse_scalar(raw_value, line_number)
        if self.position < len(self.lines) and self.lines[self.position].indent > parent_indent:
            raise RecordValidationError(
                "a scalar mapping value cannot own an indented block",
                self.lines[self.position].number,
            )
        return value

    def _parse_scalar(self, value: str, line_number: int) -> Any:
        if value.startswith('"'):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise RecordValidationError("invalid double-quoted scalar", line_number) from exc
            if not isinstance(parsed, str):
                raise RecordValidationError("quoted YAML scalar must be a string", line_number)
            return parsed
        if value.startswith("'"):
            if len(value) < 2 or not value.endswith("'"):
                raise RecordValidationError("invalid single-quoted scalar", line_number)
            return value[1:-1].replace("''", "'")
        if value.startswith(("[", "{")):
            try:
                return parse_json_without_duplicate_keys(value)
            except RecordValidationError as exc:
                raise RecordValidationError(
                    f"inline collection is outside the supported JSON-compatible subset: {exc.message}",
                    line_number,
                ) from exc
        if value.startswith(("&", "*", "!", "?", "`")):
            raise RecordValidationError(
                "anchor, alias, tag, complex key, or backtick syntax is unsupported",
                line_number,
            )
        lowered = value.lower()
        if lowered in {"null", "~"}:
            return None
        if lowered in {"true", "false"}:
            return lowered == "true"
        if self.INTEGER.fullmatch(value):
            return int(value)
        if self.FLOAT.fullmatch(value):
            return float(value)
        return value


def parse_yaml_subset(text: str) -> Any:
    return YamlSubsetParser(text).parse()


def normalized_identity(value: Any) -> str:
    if isinstance(value, (dict, list)):
        raise RecordValidationError("configured stable ID must be a scalar")
    return unicodedata.normalize("NFKC", str(value)).strip()


def walk_mappings(value: Any, path: str = "$"):
    if isinstance(value, dict):
        yield value, path
        for key, child in value.items():
            yield from walk_mappings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_mappings(child, f"{path}[{index}]")


def validate_semantics(
    value: Any,
    unique_fields: tuple[str, ...],
    enumerations: dict[str, tuple[str, ...]],
) -> list[str]:
    diagnostics: list[str] = []
    seen: dict[str, dict[str, str]] = {field: {} for field in unique_fields}
    for mapping, path in walk_mappings(value):
        for field in unique_fields:
            if field not in mapping:
                continue
            try:
                identity = normalized_identity(mapping[field])
            except RecordValidationError as exc:
                diagnostics.append(f"{path}.{field}: {exc.message}")
                continue
            if not identity:
                diagnostics.append(f"{path}.{field}: configured stable ID cannot be empty")
                continue
            normalized = identity.casefold()
            if normalized in seen[field]:
                diagnostics.append(
                    f"{path}.{field}: duplicate stable ID {identity!r}; first seen at {seen[field][normalized]}"
                )
            else:
                seen[field][normalized] = f"{path}.{field}"
        for field, allowed in enumerations.items():
            if field not in mapping:
                continue
            raw = mapping[field]
            if isinstance(raw, (dict, list)):
                diagnostics.append(f"{path}.{field}: configured enumeration value must be a scalar")
                continue
            actual = str(raw)
            if actual not in allowed:
                diagnostics.append(
                    f"{path}.{field}: invalid enumeration value {actual!r}; allowed={list(allowed)!r}"
                )
    return diagnostics


def validate_subject_binding_lists(value: Any, list_fields: tuple[str, ...]) -> list[str]:
    diagnostics: list[str] = []
    found: dict[str, int] = {field: 0 for field in list_fields}
    seen_record_ids: dict[str, str] = {}
    allowed_record_kinds = {"limitation", "unknown"}
    allowed_subject_kinds = {"artifact", "candidate", "decision"}
    drifting_subject_aliases = {"current", "latest"}

    for mapping, path in walk_mappings(value):
        for field in list_fields:
            if field not in mapping:
                continue
            found[field] += 1
            collection = mapping[field]
            collection_path = f"{path}.{field}"
            if not isinstance(collection, list):
                diagnostics.append(f"{collection_path}: subject-binding collection must be a sequence")
                continue
            for index, item in enumerate(collection):
                item_path = f"{collection_path}[{index}]"
                if not isinstance(item, dict):
                    diagnostics.append(f"{item_path}: subject-binding item must be a mapping")
                    continue
                required = (
                    "record_id",
                    "record_kind",
                    "subject_kind",
                    "subject_ref",
                    "evidence_scope_refs",
                )
                for required_field in required:
                    if required_field not in item:
                        diagnostics.append(f"{item_path}.{required_field}: required subject-binding field is missing")

                record_id = item.get("record_id")
                if record_id is not None:
                    try:
                        identity = normalized_identity(record_id)
                    except RecordValidationError:
                        diagnostics.append(f"{item_path}.record_id: record identity must be a scalar")
                    else:
                        if not identity:
                            diagnostics.append(f"{item_path}.record_id: record identity cannot be empty")
                        else:
                            normalized = identity.casefold()
                            if normalized in seen_record_ids:
                                diagnostics.append(
                                    f"{item_path}.record_id: duplicate subject-binding record ID {identity!r}; first seen at {seen_record_ids[normalized]}"
                                )
                            else:
                                seen_record_ids[normalized] = f"{item_path}.record_id"

                record_kind = item.get("record_kind")
                if record_kind is not None:
                    if not isinstance(record_kind, str) or record_kind not in allowed_record_kinds:
                        diagnostics.append(
                            f"{item_path}.record_kind: invalid value {record_kind!r}; allowed={sorted(allowed_record_kinds)!r}"
                        )

                subject_kind = item.get("subject_kind")
                if subject_kind is not None:
                    if not isinstance(subject_kind, str) or subject_kind not in allowed_subject_kinds:
                        diagnostics.append(
                            f"{item_path}.subject_kind: invalid value {subject_kind!r}; allowed={sorted(allowed_subject_kinds)!r}"
                        )

                subject_ref = item.get("subject_ref")
                if subject_ref is not None:
                    try:
                        normalized_ref = normalized_identity(subject_ref)
                    except RecordValidationError:
                        diagnostics.append(f"{item_path}.subject_ref: subject reference must be a scalar")
                    else:
                        if not normalized_ref:
                            diagnostics.append(f"{item_path}.subject_ref: subject reference cannot be empty")
                        elif normalized_ref.casefold() in drifting_subject_aliases:
                            diagnostics.append(
                                f"{item_path}.subject_ref: drifting alias {normalized_ref!r} is not a stable subject identity"
                            )

                evidence_refs = item.get("evidence_scope_refs")
                if evidence_refs is not None:
                    if not isinstance(evidence_refs, list) or not evidence_refs:
                        diagnostics.append(
                            f"{item_path}.evidence_scope_refs: evidence scope references must be a non-empty sequence"
                        )
                    else:
                        seen_refs: set[str] = set()
                        for ref_index, raw_ref in enumerate(evidence_refs):
                            ref_path = f"{item_path}.evidence_scope_refs[{ref_index}]"
                            try:
                                normalized_ref = normalized_identity(raw_ref)
                            except RecordValidationError:
                                diagnostics.append(f"{ref_path}: evidence scope reference must be a scalar")
                                continue
                            if not normalized_ref:
                                diagnostics.append(f"{ref_path}: evidence scope reference cannot be empty")
                                continue
                            folded = normalized_ref.casefold()
                            if folded in seen_refs:
                                diagnostics.append(f"{ref_path}: duplicate evidence scope reference {normalized_ref!r}")
                            else:
                                seen_refs.add(folded)

    for field in list_fields:
        if found[field] == 0:
            diagnostics.append(f"$: configured subject-binding list not found: {field}")
        elif found[field] > 1:
            diagnostics.append(
                f"$: configured subject-binding list {field!r} appears {found[field]} times; use one explicit collection"
            )
    return diagnostics


def parse_enum_specs(values: list[str]) -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}
    for value in values:
        field, separator, raw_allowed = value.partition("=")
        allowed = tuple(item for item in raw_allowed.split(",") if item)
        if not separator or not field or not allowed:
            raise RecordValidationError(
                f"invalid --enum-field {value!r}; expected FIELD=VALUE1,VALUE2"
            )
        if field in result:
            raise RecordValidationError(f"duplicate --enum-field specification: {field}")
        result[field] = allowed
    return result


def validate_file(
    path: Path,
    unique_fields: tuple[str, ...],
    enumerations: dict[str, tuple[str, ...]],
    subject_binding_lists: tuple[str, ...],
) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [{"file": str(path), "line": None, "message": f"cannot read UTF-8 input: {exc}"}]

    try:
        suffix = path.suffix.lower()
        if suffix == ".json":
            value = parse_json_without_duplicate_keys(text)
        elif suffix in {".yaml", ".yml"}:
            value = parse_yaml_subset(text)
        else:
            raise RecordValidationError("unsupported file extension; expected .yaml, .yml, or .json")
    except RecordValidationError as exc:
        return [{"file": str(path), "line": exc.line, "message": exc.message}]

    for message in validate_semantics(value, unique_fields, enumerations):
        diagnostics.append({"file": str(path), "line": None, "message": message})
    for message in validate_subject_binding_lists(value, subject_binding_lists):
        diagnostics.append({"file": str(path), "line": None, "message": message})
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate explicitly routed operational YAML/JSON without rewriting it."
    )
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--unique-field", action="append", default=[])
    parser.add_argument("--enum-field", action="append", default=[])
    parser.add_argument("--subject-binding-list", action="append", default=[])
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    unique_fields = tuple(dict.fromkeys(args.unique_field))
    if len(unique_fields) != len(args.unique_field):
        parser.error("duplicate --unique-field specification")
    subject_binding_lists = tuple(dict.fromkeys(args.subject_binding_list))
    if len(subject_binding_lists) != len(args.subject_binding_list):
        parser.error("duplicate --subject-binding-list specification")
    try:
        enumerations = parse_enum_specs(args.enum_field)
    except RecordValidationError as exc:
        parser.error(exc.message)

    diagnostics: list[dict[str, Any]] = []
    for path in args.files:
        diagnostics.extend(validate_file(path, unique_fields, enumerations, subject_binding_lists))
    diagnostics.sort(
        key=lambda item: (
            item["file"],
            item["line"] if item["line"] is not None else -1,
            item["message"],
        )
    )
    payload = {
        "status": "failed" if diagnostics else "passed",
        "files": [str(path) for path in args.files],
        "unique_fields": list(unique_fields),
        "enumerations": {key: list(value) for key, value in sorted(enumerations.items())},
        "subject_binding_lists": list(subject_binding_lists),
        "diagnostics": diagnostics,
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    elif diagnostics:
        for item in diagnostics:
            location = item["file"]
            if item["line"] is not None:
                location += f":{item['line']}"
            print(f"{location}: {item['message']}", file=sys.stderr)
    else:
        print(f"operational record validation: passed ({len(args.files)} file(s))")
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main())
