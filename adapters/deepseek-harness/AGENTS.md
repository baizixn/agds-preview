# AGDS Preview in DeepSeek Harness

Use the project-local skills under `.dsh/skills`. Load the matching skill before reporting or changing an exercise. If the skill tool clips a long result, read its `SKILL.md` in smaller ranges, then read the linked references relevant to the task.

For the Unity exercise, start with `examples/FishingShelter/README.md`. The starter and reference scenes, original Blender file and automated checks are the exercise evidence. Keep their source and acceptance status distinct. A first inspection is read-only. Write only after the user authorizes a change and identifies the permitted exercise files.

For a task requiring independent review, use a separate review session with an effective read-only permission mode. The review skill guides the decision; the host permission mode enforces the available tools. Preserve owner approval boundaries and report which checks actually ran.
