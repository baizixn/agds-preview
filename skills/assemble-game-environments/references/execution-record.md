# Scene write record

For a substantial assembly, record just the spatial decision owner, the single scene writer and the specification reference. A function may be fulfilled by the same person. Use the task's actual assignee identifiers, not an invented claim of acceptance.

```json
{
  "decision_owner": "assigned-executor",
  "writer": "assigned-executor",
  "specification": null
}
```

`specification` is null while missing; once available it is a path relative to this record (or an absolute path) to the task's approved placement requirements. The requirements identify the target scene/objects, coordinate frame and the position, rotation, scale or contact constraints needed for this action. Preserve approval provenance already present in the task; file existence does not establish approval or tool suitability.

Before invoking the scene-writing tool, run:

```
python scripts/check_scene_handoff.py --record <record.json> --writer <actual-assignee>
```

The helper is read-only. Exit 2 / `pending` means stop before any scene write and return the missing field. Exit 0 / `ready` identifies the specification bytes and assigned writer, not a production or approval pass. The writer reads that exact specification, verifies its hash is unchanged at execution, and checks the already authorized target, writable scope and tool route. If the specification is incomplete for the requested action, keep it pending rather than inventing transforms. Only the assigned writer operates the scene; changed spatial requirements return to the decision owner.

After writing, return the applied object transforms, saved scene identity and requested reopen evidence to the decision owner; they may be the same executor. QA can inspect this evidence without becoming a second writer. Do not infer runtime, visual fidelity or performance from a save/reopen receipt.

For an approved small move, reuse the existing instruction in one sentence, for example: “The assigned executor applies the approved 0.1-unit rightward move and returns the affected view.” Do not require a JSON record, another role or a new approval merely for that small action.
