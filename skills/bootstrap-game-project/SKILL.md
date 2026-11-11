---
name: bootstrap-game-project
description: Create or repair the baseline local structure that lets a game project work with AI Game Development Studio, including AGENTS.md, consolidated Game_Documents, separate AI_Records, a local operating agreement, context routing, tasks, approvals, feedback, handoffs, and clean information tiers. Use when starting a new game repository, onboarding an existing project, or standardizing its collaboration and documentation structure.
---

# Bootstrap Game Project

Create a game-owned project structure. Do not put game content in the AI Game Development Studio plugin.

## Workflow

1. Inspect the target root, existing repository rules, documents, engine, platform, and whether it is a Git worktree, an SVN working copy, or unmanaged.
2. Preserve existing files. Identify conflicts instead of overwriting them.
3. Run `scripts/bootstrap_game_project.py` without `--apply` to preview the generated paths.
4. Review the preview against the existing project and requested scope.
5. Run with `--apply` only after the target root and project metadata are correct.
6. Merge existing content deliberately; never replace a mature project structure with the template blindly.
7. Validate YAML, links, and required entry files. Check Git or SVN status only when that version-control system is actually present; an unmanaged directory requires no commit.
8. Return the created files, conflicts, assumptions, and first approval item.

## Ownership

This is a Studio foundation skill, not a game-engineering domain skill. The Studio Orchestrator normally invokes it; an Engineering Agent may execute or modify its deterministic script, while the Project Owner approves structural policy.

Read `references/structure-policy.md` before onboarding an existing project.
