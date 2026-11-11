# Archify 3.2.0: bounded local validation

Date: 2026-10-22 (Asia/Shanghai). This record describes a local compatibility check for the optional external Skill. It does not bundle Archify into AGDS or make diagram creation mandatory.

## Identity

- Official release: [v3.2.0](https://github.com/tt-a1i/archify/releases/tag/v3.2.0).
- Source commit: `208acba8d412335185b2056fedf54b3405df43fb`; package `3.2.0`, Skill metadata `3.2`.
- Official `archify.zip` SHA-256: `70e210265c59f24dcbdf2a502ff671104b5454e7ee7d3554aecd86bad32384f5`, checked against the release asset digest.
- Independently installed Skill: 200 shipped files match the release archive. A complete 315-file old 3.0.1 installation was backed up and hash-verified before replacement. Different package file counts do not authorize merging versions.

## Finite acceptance matrix

Use only game-agnostic upstream examples copied unchanged from the backed-up 3.0.1 package. They illustrate authored relationships, not the actual AGDS runtime.

| Check | Evidence scope |
| --- | --- |
| Original compatibility case | `agent-tool-call.workflow.json` (schema v2), SHA-256 `d67965d50872c97e4ff3476271e645bf19fab6b3ab44e111bdb44b063e3aa36f`; 3.2.0 finalize passes validate, deliver, strict check and real-browser check. |
| Unaffected diagram mode | `web-app.architecture.json`, SHA-256 `95e051b27a9e4a3307e194c0f666fca4af51470be7e2228d400ff48aea5b353b`; the same four gates pass. A route-detour advisory remains and is not silently relabelled as a failure or a layout repair. |
| Actual browser exports | Pass: both examples opened in Chrome; the page's export menu downloaded PNG in light and dark themes. All four PNGs have valid signatures and dimensions, with zero page errors. Downloads are separate evidence from screenshots. |
| Visual inspection | Completed for the four downloaded PNGs: labels and diagram bounds are complete, with no viewer controls in the exports. The architecture detour remains visible. This is limited to those views, not general design approval. |
| Optional-tool boundary | AGDS continues to discover the installed `archify` Skill, permits other sufficient representations and requires authorization for installation or update. No renderer, host-specific executable path or game evidence is copied into AGDS. |
| Repeat and protection | Verify unchanged input hashes, preserved backup hashes and installed-file identity after checks. Plugin packaging permits only the declared documentation and version changes over the previous installed baseline. |

Raw synthetic-case receipts and plugin-install verification are retained in the Owner's local release evidence for this date; they are not required in the distributed Skill or committed to Git. The bounded results above are the portable summary. Local captures and backup paths stay in host-local evidence.

## Evidence limits

This is not coverage of all ten diagram types, new explainer pages, every export format, every browser, other team machines, old-session hot reload, live game behavior or professional correctness. PNG export does not replace deterministic delivery. No automatic diagram/project synchronization is introduced. Preserve 3.0.1 historical receipts; do not update their version labels or claim they ran 3.2.0.
