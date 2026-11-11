# Agent catalog

Agents are temporary, bounded workers created for a task. They are not persistent services and do not own final decisions.

`Agent_System/Agent_Registry.yaml` is the authority for which custom Agent definitions are active in the current Wave. Roles listed here but absent from that Registry remain roadmap roles; use their existing Skills only when the task requires them, and do not represent them as implemented custom Agents.

| Agent | Primary skill | Produces | Cannot approve |
| --- | --- | --- | --- |
| Studio Orchestrator | `studio-orchestrator` | task routing, synthesis, approval request | its own directional proposal |
| Producer | `produce-game-project` | stage-appropriate value/learning plan and evidence-based Go/Adjust/Stop review | scope, milestone, stage policy, or quality-bar changes |
| Game Designer | `design-game` | stage-appropriate falsifiable gameplay candidates and observation decisions | target-player framing or game direction |
| Engineering Agent | `engineer-game` | technical plan, implementation, impact and verification evidence | product requirements |
| Art Director | `direct-game-art`, `produce-game-2d-art`, `produce-game-3d-assets`, `produce-game-realtime-art`, `produce-game-static-character-hair`, `assemble-game-environments` | thin direction, production brief, visual criteria and critique; named task-scoped executor produces; Engineering receives technical work; QA verifies; Reviewer independently reviews; Owner adopts; ownership does not grant invocation (`invokable_skills=[]`). Environment assembly requires a named scene executor and does not certify a production tool, target platform, or reference match. The hair route is isolated editable static coarse root/crown repair only, and does not change rigid/static non-character 3D or establish full mesh-topology transfer, rig, animation, runtime, or performance capability. | final visual direction, self-approval, technical or QA verdicts, Candidate approval or installation |
| Audio Director | `direct-game-audio` | audio candidates, cue plan, review | final audio direction |
| Audio Production | `produce-game-audio-assets`, `integrate-interactive-audio` | traceable audio assets or bounded interactive-audio implementation evidence | audio direction, production-code architecture, independent QA acceptance, rights, scope, or final acceptance |
| QA Lead Agent | `assure-game-quality` | traceable tests, findings, evidence states, and build-acceptance recommendation | fixes, quality bars, or final release decisions |
| Memory Keeper | `manage-project-memory` | state, handoff, decision and approval records | content decisions |
| Project Bootstrapper | `bootstrap-game-project` | new-project collaboration and documentation foundation | project direction or replacement of existing content |
| Capability Curator | `evolve-studio-capabilities` | evidence-backed Agent and Skill improvement candidate | shared capability promotion |
| Reviewer | `review-candidate` | independent Candidate review, risks, missing evidence, recommendation | final acceptance or rejection |

For independent review, use a fresh Reviewer and do not pass the author's reasoning or requested verdict. Reviewer recommendations remain Candidate input for the Project Owner.
