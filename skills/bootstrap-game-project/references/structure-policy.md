# Structure policy

## Required separation

- Plugin repository: reusable Agent and Skill behavior only.
- Game repository: all game content, project facts, evidence, tasks, approvals, and feedback.
- `Game_Documents/`: all human-facing game facts and domain documents.
- `AI_Records/`: compact operational records, not full design documents.

## Existing project onboarding

Read existing rules and indexes first. Generate missing pieces only. When a canonical file already exists under another name, update the context map instead of creating a duplicate fact source.

## Default information tiers

- Formal domain documents: approved project facts.
- `Agent_Records/Working`: incomplete and disposable.
- `Agent_Records/Candidate`: reviewable but unapproved.
- `Agent_Records/Approved`: approved Agent results and promotion evidence.
- `Game_Documents/Archive` or `AI_Records/Archive`: create only for superseded material that retains traceability value; do not generate placeholder-only archives.
