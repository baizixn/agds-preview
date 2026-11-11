
"""Build the DeepSeek Harness Preview ZIP from a committed AGDS Preview tree."""

from argparse import ArgumentParser
from hashlib import sha256
from io import BytesIO
from pathlib import Path, PurePosixPath
import json
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


PACKAGE = "AGDS-Preview-DeepSeekHarness"
PLUGIN_SOURCE = "adapters/deepseek-harness/plugin/"
SOURCE_PATHS = (
    PLUGIN_SOURCE.rstrip("/"), "examples", "PREVIEW-TERMS-DRAFT.md",
    "README.deepseek-harness.md", "adapters/deepseek-harness/AGENTS.md",
)
SKILLS = (
    "assemble-game-environments",
    "assure-game-quality",
    "bootstrap-game-project",
    "design-game",
    "direct-game-art",
    "direct-game-audio",
    "engineer-game",
    "evolve-studio-capabilities",
    "integrate-interactive-audio",
    "manage-project-memory",
    "produce-game-2d-art",
    "produce-game-3d-assets",
    "produce-game-audio-assets",
    "produce-game-project",
    "produce-game-realtime-art",
    "produce-game-static-character-hair",
    "review-candidate",
    "studio-orchestrator",
)

def git(root, *args):
    return subprocess.check_output(["git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "-C", str(root), *args])


def make_package(root):
    commit = git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    blob = git(root, "archive", "--format=zip", commit, *SOURCE_PATHS)
    with ZipFile(BytesIO(blob)) as archive:
        original = {member.filename: archive.read(member)
                    for member in archive.infolist() if not member.is_dir()}

    files = {
        "plugin/" + name.removeprefix(PLUGIN_SOURCE) if name.startswith(PLUGIN_SOURCE) else name: data
        for name, data in original.items()
    }
    version = json.loads(files["plugin/package.json"])["version"]
    files["README.md"] = files.pop("README.deepseek-harness.md")
    files["AGENTS.md"] = files.pop("adapters/deepseek-harness/AGENTS.md")
    discovered = tuple(sorted(PurePosixPath(name).parts[2] for name in files
                              if name.startswith("plugin/skills/") and name.endswith("/SKILL.md")))
    if discovered != SKILLS:
        raise ValueError(f"Unexpected plugin skills: {discovered}")
    if "plugin/skills/studio-orchestrator/references/task-learning.md" not in files:
        raise ValueError("Engineering skill reference is missing.")
    manifest = {"package": version, "sourceCommit": commit, "hostTarget": "0.2.2-rc.1",
                "skillRoot": "plugin/skills", "skills": discovered,
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
