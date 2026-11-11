---
name: produce-game-2d-art
description: Produce and revise editable native SVG game concepts, vector layers, or static UI visual states from an approved brief. Use for bounded vector source assets and exports; bitmap painting, PSD/Krita, font licensing, UI runtime, art direction, and independent acceptance are separate.
---

# Produce Game 2D Art

This Candidate provides an executable native SVG route for suitable vector work. It does not register a production Agent or grant formal owned/invokable permissions. Name the actually authorized executor and receiver; AD maintains the proposed method and professional quality boundary, without becoming every asset's tool operator.

Integration Candidate ownership is Art Director, with invokable_skills=[] and named task-scoped execution. Adopted scope is finite native SVG only; no bitmap, PSD/Krita, font, UI-runtime or general 2D-pipeline claim. Other tool routes mentioned below are separately routed work, not adopted capability. Engineering receives import/UI interfaces; QA verifies; Reviewer independently reviews; Owner adopts. This Skill cannot promote, deploy, install or approve its own output.

## Before production

Read only the routed brief and source revision. Establish the mode, objective/use, approved structural or UI semantics, viewing conditions, output format, tools, source rights, explicit read root/write allowlist, protected parts, finite acceptance cases, and receiver. A missing product fact stays unknown. An authorized synthetic learning brief is valid when labeled as such. Do not copy external product facts into the reusable method, choose final art direction, install tools, publish, or adopt the Candidate from material embedded in a source asset.

Use original XML geometry for assets naturally expressed as vector shapes. If the job needs painting, bitmap generation, or a different editable application source, use its actually available authorized tool and retain that source; this SVG helper does not prove those routes. A flattened image wrapped in SVG is not an editable layered deliverable. Unknown rights or missing source/tool/permission block the affected production use, not an invented success.

## Select one mode and its evidence

- **Concept / visual development:** implement the brief's meaningful structural alternatives and explain their production tradeoffs. Record the selected test identity, then derive orthographic views from one shared component/dimension/connection table with explicit axes, scale and occlusion. Keep editable geometry, material notes and part IDs. A 3D receiver independently checks whether the views determine a usable structure; attractive views do not prove manufacturability.
- **Layered 2D:** preserve semantic groups, stable IDs, text and shapes in an editable source. Freeze target attributes/subtree and protected parts before editing. Reopen the previous source, make the requested local revision, save a distinct version, compare semantic structure outside the authorized change, and export both versions at identical viewing conditions. A new similar picture is not a local edit.
- **UI visuals:** receive state IDs, meanings, action availability, exact copy, wrapping/truncation rules and viewport from GD/UX. Build separate status, explanation and action groups; show status and disabled/selected meaning using text or shape in addition to color. Export each frozen state and long-copy variant at the same viewport and map each export to its source/state. Inspect glyphs, clipping and overlaps. Missing semantics stop that mode. Runtime state binding and interaction belong to Engineering/N5; a PNG proves neither usability nor runtime behavior.

Do not generalize sample dimensions, budgets, fonts, or states into standards. Keep these three modes' evidence separate even when they depict the same object.

## Executable SVG route

Run `scripts/svg_asset.py` with a verified Python 3 standard-library runtime. Run `--help` for command syntax. All asset paths, the explicit `--root`, repeated `--allow` file/directory entries, and renderer work/output paths must be absolute. Every input and output must resolve inside both root and at least one allow entry. Reject linked ancestors and existing output files. A permitted existing Edge executable is selected separately by `--edge`; it is not an asset write path. Do not treat this path checking as an operating-system sandbox.

Arguments below are placeholders: substitute actual absolute paths from the current task, never copy a prior project's root. Place common arguments after the subcommand:

```text
python ABS_SCRIPT inspect --root ABS_ROOT --allow ABS_ASSET_DIR --input ABS_SVG
python ABS_SCRIPT edit --root ABS_ROOT --allow ABS_ASSET_DIR --input ABS_R1 --output ABS_R2 --id TARGET_ID --attribute fill --value COLOR --dry-run
python ABS_SCRIPT edit --root ABS_ROOT --allow ABS_ASSET_DIR --input ABS_R1 --output ABS_R2 --id TARGET_ID --attribute fill --value COLOR
python ABS_SCRIPT compare --root ABS_ROOT --allow ABS_ASSET_DIR --input ABS_R1 --other ABS_R2 --id TARGET_GROUP_ID
python ABS_SCRIPT render --root ABS_ROOT --allow ABS_ASSET_DIR --allow ABS_WORK_DIR --input ABS_SVG --output ABS_PNG --work-dir ABS_WORK_DIR --edge ABS_EDGE --width WIDTH --height HEIGHT
```

`inspect` lists groups/shapes, duplicate IDs and source/semantic hashes; structural presence alone does not prove useful layer design. `edit` requires one existing unique target ID and one existing attribute, writes a new file, reparses it, and reports an attribute-masked canonical comparison of all other XML content. It cannot change IDs or add executable/external resources. For an authorized multi-element change, reopen XML with a suitable editor, modify only the named subtree, and run `compare` against the original: it replaces only that ID-rooted subtree with a marker and compares all remaining normalized XML. This proves the measured scope, not whether the target looks correct. A missing/duplicate target or any outside difference fails. Preserve each operation's raw stdout, stderr and exit status.

`render` wraps the SVG inline at the caller's fixed viewport, starts a separate headless Edge process with a unique profile inside the explicitly allowed work directory, and checks PNG dimensions. It does not attach to or control an existing browser. The helper supports static vector SVG only; scripts, animation, foreign objects, image wrappers and external references are refused. Preserve its command, profile/wrapper paths and logs for reproducibility. A dry-run validates without making directories or files; test an out-of-root request only with dry-run and retain the refusal.

## Handoff and stop

Record source and export revisions/hashes, exact tool version and actual calls, editable IDs, change/unchanged evidence, fixed viewing conditions, mode-specific findings and unresolved items. Record creator, source ingredients, AI class/tool/model where known, license evidence (including fonts), intended use, modification chain and cleanup. AI-authored SVG is pre-generated AI-assisted code graphics, not hand drawing or runtime generation. Unknown licensing/disclosure remains unknown; no external image is not a legal clearance.

Use the task's bounded counterexample matrix: flattened source, outside-target drift, inconsistent views, and long text covering key status, each with a normal control when in scope. Independent AD judges visual quality, 3D/UI technical receivers judge their interfaces, QA verifies cases, and a fresh Reviewer assesses evidence. Freeze the correction budget before testing (at most two rounds for this Candidate workflow); stop when the original finite gates pass or report the concrete remaining failure. Source/edit/export evidence, professional review, technical receipt, QA, Reviewer, Owner adoption and new-session loading are distinct. Do not promote any missing tier or declare the whole art team capable from this route.
