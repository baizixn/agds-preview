
"""Build the DeepSeek Harness Preview ZIP from a committed AGDS Preview tree."""

from argparse import ArgumentParser
from hashlib import sha256
from io import BytesIO
from pathlib import Path, PurePosixPath
import json
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


PACKAGE = "AGDS-Preview-DeepSeekHarness"
SOURCE_PATHS = (
    "skills", "examples", "PREVIEW-TERMS-DRAFT.md", ".codex-plugin/plugin.json",
    "README.deepseek-harness.md", "adapters/deepseek-harness/AGENTS.md",
)
SKILLS = (
    "assure-game-quality", "bootstrap-game-project", "engineer-game",
    "manage-project-memory", "review-candidate",
)


def git(root, *args):
    return subprocess.check_output(["git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "-C", str(root), *args])


def make_package(root):
    commit = git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    blob = git(root, "archive", "--format=zip", commit, *SOURCE_PATHS)
    with ZipFile(BytesIO(blob)) as archive:
        original = {member.filename: archive.read(member)
                    for member in archive.infolist() if not member.is_dir()}

    version = json.loads(original.pop(".codex-plugin/plugin.json"))["version"] + "-dsh.1"
    files = {".dsh/" + name if name.startswith("skills/") else name: data
             for name, data in original.items()}
    files["README.md"] = files.pop("README.deepseek-harness.md")
    files["AGENTS.md"] = files.pop("adapters/deepseek-harness/AGENTS.md")
    discovered = tuple(sorted(PurePosixPath(name).parts[2] for name in files
                              if name.startswith(".dsh/skills/") and name.endswith("/SKILL.md")))
    if discovered != SKILLS:
        raise ValueError(f"Unexpected project skills: {discovered}")
    if ".dsh/skills/studio-orchestrator/references/task-learning.md" not in files:
        raise ValueError("Engineering skill reference is missing.")
    manifest = {"package": version, "sourceCommit": commit, "hostTarget": "0.2.2-rc.1",
                "skillRoot": ".dsh/skills", "skills": discovered,
                "sha256": {name: sha256(data).hexdigest() for name, data in sorted(files.items())}}
    files["preview-manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()

    result = BytesIO()
    with ZipFile(result, "w") as archive:
        for name, data in sorted(files.items()):
            entry = ZipInfo(f"{PACKAGE}/{name}")
            archive.writestr(entry, data, compress_type=ZIP_DEFLATED)
    with ZipFile(result) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity check failed.")
    return result.getvalue()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = make_package(Path(__file__).resolve().parents[2])
    with args.output.open("xb") as file:
        file.write(payload)
    print(f"SHA-256 {sha256(payload).hexdigest()}  {args.output}")


if __name__ == "__main__":
    main()
