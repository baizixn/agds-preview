# Project contract routing

Use this decision order when a target project does not have the current default `AI_Records/` entry point.

1. If `AI_Records/` exists, read its state and context map.
2. If only `AI_Studio/` exists, treat it as a legacy project record system. Do not create `AI_Records/`; invoke `bootstrap-game-project` for a migration preview and Owner approval.
3. If equivalent project documents exist under other names, preserve them and route the context map to the canonical locations.
4. If no project records exist, invoke `bootstrap-game-project` in preview mode.

Never create a second state system, apply a migration, replace mature documents, or initialize version control without explicit authorization.
