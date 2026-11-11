from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import subprocess


TOKENS = {
    "{{DATE}}": lambda args: date.today().isoformat(),
    "{{PROJECT_NAME}}": lambda args: args.project_name,
    "{{ENGINE}}": lambda args: args.engine,
    "{{PLATFORM}}": lambda args: args.platform,
}


def render(text: str, args: argparse.Namespace) -> str:
    for token, value in TOKENS.items():
        text = text.replace(token, value(args))
    return text


def collect(template_root: Path) -> list[Path]:
    return sorted(path for path in template_root.rglob("*") if path.is_file())


def detect_version_control(target_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(target_root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "true":
            return "git"
    except FileNotFoundError:
        pass

    for path in (target_root, *target_root.parents):
        if (path / ".svn").is_dir():
            return "svn"
    return "unmanaged"


def detect_state_structure(target_root: Path) -> tuple[str, list[Path]]:
    detected: list[tuple[str, Path]] = []
    native = target_root / "AI_Records"
    if native.is_dir():
        detected.append(("native-ai-records", native))

    legacy = target_root / "AI_Studio"
    if legacy.is_dir():
        detected.append(("legacy-ai-studio", legacy))

    markers = {"PROJECT_STATE.md", "ACTIVE_TASKS.yaml", "CONTEXT_MAP.md"}
    if target_root.is_dir():
        children = sorted(
            (path for path in target_root.iterdir() if path.is_dir()),
            key=lambda path: str(path).lower(),
        )
        grandchildren = sorted(
            (path for child in children for path in child.iterdir() if path.is_dir()),
            key=lambda path: str(path).lower(),
        )
        for directory in (target_root, *children, *grandchildren):
            if directory in {native, legacy}:
                continue
            if markers.issubset({path.name for path in directory.iterdir() if path.is_file()}):
                detected.append(("equivalent-custom", directory))

    if not detected:
        return "none", []
    if len(detected) == 1:
        return detected[0][0], [detected[0][1]]
    kinds = ",".join(kind for kind, _ in detected)
    return f"ambiguous[{kinds}]", [path for _, path in detected]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview or create an AI Game Development Studio project foundation without overwriting files."
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--engine", default="Undecided")
    parser.add_argument("--platform", default="Undecided")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    target_root = Path(args.project_root).expanduser().resolve()
    template_root = Path(__file__).resolve().parents[1] / "assets" / "project-template"
    if not template_root.is_dir():
        raise SystemExit(f"Template not found: {template_root}")

    version_control = detect_version_control(target_root)
    structure_kind, structure_paths = detect_state_structure(target_root)
    blocks_parallel_state = structure_kind in {"legacy-ai-studio", "equivalent-custom"} or structure_kind.startswith(
        "ambiguous["
    )

    files = collect(template_root)
    conflicts: list[Path] = []
    pending: list[tuple[Path, Path]] = []
    for source in files:
        relative = source.relative_to(template_root)
        target = target_root / relative
        if target.exists():
            conflicts.append(relative)
        else:
            pending.append((source, target))

    mode = "APPLY" if args.apply else "PREVIEW"
    print(f"Mode: {mode}")
    print(f"Target: {target_root}")
    print(f"Version control: {version_control}")
    print(f"State structure: {structure_kind}")
    for structure_path in structure_paths:
        print(f"State path: {structure_path}")
    if blocks_parallel_state:
        print("BLOCK  equivalent project state exists; migration approval is required")
    for _, target in pending:
        print(f"CREATE {target.relative_to(target_root)}")
    for relative in conflicts:
        print(f"KEEP   {relative}")

    if args.apply and blocks_parallel_state:
        print("Created: 0")
        print(f"Conflicts preserved: {len(conflicts)}")
        return 2

    if args.apply:
        target_root.mkdir(parents=True, exist_ok=True)
        for source, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            content = source.read_text(encoding="utf-8")
            target.write_text(render(content, args), encoding="utf-8", newline="\n")

    print(f"Created: {len(pending) if args.apply else 0}")
    print(f"Conflicts preserved: {len(conflicts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
