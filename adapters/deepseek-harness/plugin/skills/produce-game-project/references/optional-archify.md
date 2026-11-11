# Optional Archify diagrams

AGDS supports Archify as an independently installed drawing Skill, alongside Mermaid and other available tools. It is not bundled, required, or automatically installed. Choose the tool that explains this question accurately and clearly with reasonable effort; do not impose a diagram-size threshold, mandatory pair of diagrams, or extra role handoff. A concise Mermaid diagram or prose may be the complete result.

Archify provides explorable standalone HTML with node focus, authored-path tracing and editable JSON. Professional authors still own the plans, relationships and source claims. A renderer or browser pass proves the artifact checks it actually ran, not implementation correctness, runtime behavior or user understanding.

## Discover and use

When the task benefits from Archify or the user requests it, select the available `archify` Skill from the current host's skills catalog and follow its actual `SKILL.md`. Resolve the CLI relative to that installed Skill, not a contributor's machine path or a historical trial directory. Do not reimplement its viewer or copy its full instructions here.

If it is absent, say so and use a sufficient available representation, or install it when the user has authorized installation. A missing optional tool does not block ordinary AGDS work. Do not silently replace an explicit Archify request with another tool and claim Archify was used.

Example requests:
- “用 Archify 画出这个已说明方案的主流程、取消与重试路径，保留提议和未知项，给我可打开的结果和可编辑源。”
- “解释这三个模块的关系；工具由你选，以清楚、省事为准。”

Keep output in the requesting project's authorized artifact location. Game-specific diagrams and evidence belong to that game, not shared AGDS. A plan remains a plan; repository-backed diagrams must follow the installed Skill's source-evidence rules. In the verified version, Git source evidence binds committed bytes at one revision, not uncommitted working-tree edits. Unsupported web forges need the supported local-only source mode; do not invent public links.

For a delivered artifact, report the actual HTML and editable source, checks completed, browser evidence and any visual review separately. Keep dates/versions and unresolved sources when they affect the reading. Update a diagram or mark stale portions when its underlying plan changes; this integration provides no automatic project synchronization.

## Install or update by choice

Verified upstream identity: [tt-a1i/archify v3.2.0](https://github.com/tt-a1i/archify/releases/tag/v3.2.0), directory `archify/`, commit `208acba8d412335185b2056fedf54b3405df43fb`, package `3.2.0` (Skill metadata `3.2`). See the [bounded validation record](archify-3.2.0-validation.md). This records the tested revision; it is not a claim about the newest release or every diagram type. Upstream uses MIT; retain supplied license and notices when redistributing it. Earlier 3.0.1 evidence remains historical and is not relabelled as 3.2.0 evidence.

In Codex, use the available `skill-installer` Skill with this repository, path and exact ref. Its supported helper accepts:

```text
install-skill-from-github.py --repo tt-a1i/archify --path archify --ref 208acba8d412335185b2056fedf54b3405df43fb
```

Locate the helper from the current `skill-installer`; this is an argument example, not a shell command assuming it is on PATH. It must not overwrite an existing installation. For another host, use its supported skill installer with the same pinned source. New installation should be checked in a fresh context, not assumed hot-loaded in an existing chat.

For an authorized update, first preserve the complete old installation and verify a per-file hash manifest. Stage the new version separately, confirm its identity, then replace only the exact independently installed Skill directory, retaining a recoverable old copy and authored diagrams. If a source download fails, the official v3.2.0 release asset `archify.zip` is an alternative: its published SHA-256 is `70e210265c59f24dcbdf2a502ff671104b5454e7ee7d3554aecd86bad32384f5`. Verify the archive and reject unsafe extraction paths before use. Check an unchanged old input through generation, a real browser and the required export before considering the update locally verified; a successful download alone is insufficient.

Core tooling requires Node.js 18+; the complete automated handoff also needs a supported Chrome/Chromium browser. Follow upstream diagnostics if a check cannot run, preserving the actual failure. Optional update reminders are upstream behavior, not permission to update; `ARCHIFY_UPDATE_CHECK_DISABLED=1` disables update-check networking for an individual execution when desired. Do not change global environment settings merely to draw a diagram.

AGDS updates and Archify updates have independent identities. Test a chosen update before adopting it; AGDS does not auto-install or auto-upgrade it. To stop using Archify, leave it uninvoked and continue with another tool. Uninstall only its independently installed directory through a supported host operation, after confirming the exact path and preserving authored diagrams.
