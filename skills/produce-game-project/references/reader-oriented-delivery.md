# Reader-oriented production delivery

Use this reference for a production-owned explanation, handoff, status document, or external-facing brief. Apply only the choices that help the intended reader. A short answer may be the complete deliverable.

## Choose the reading task

Infer the audience and purpose from the request and available context: what should the reader understand, decide, or do? Resolve ordinary choices yourself; ask only when a material unknown prevents a useful result. Internal/external labels alone do not determine length, tone, or technical depth.

For internal continuation, make the relevant current state, unresolved work, dependencies, responsibility, and next decision understandable without requiring the reader to reconstruct logs. For external use, organize around that audience's purpose and retain limitations that affect their decision. These are examples of reading tasks, not required section lists. Do not turn internal records into an external brief by merely deleting technical words.

Preserve source authority: observed, proposed, verified, and unknown claims remain distinct in prose and diagrams. Missing facts stay missing. Producer assembles the explanation; specialists own professional conclusions, QA owns test results, and Owner decides adoption. A clearer rewrite cannot upgrade any of them.

## Write for people

For human-facing deliverables, use familiar words and direct sentences. Remove repetition, ceremony, and empty claims. Explain necessary technical terms where they first affect understanding; retain exact names where readers need them to act or verify. Expand reasons, conditions, steps, exceptions, and evidence only to the depth needed for the reading task. Concise does not mean omitting a necessary explanation. Internal machine-oriented Markdown records may keep their required fields; file extension alone does not make a document machine-facing.

## Choose a representation

Use prose for reasoning, a table for comparable facts, and a diagram when spatial relations reduce explanation cost. Start from the question, not a quota of diagram types. Possible choices include a mind map for topic hierarchy, an architecture view for responsibility and dependencies, a sequence for ordered messages and alternatives, and a swimlane for handoffs and returns. This list is illustrative; no diagram is required when prose suffices.

State the diagram's scope and whether it describes current behavior or a proposal. Keep labels consistent with the prose; distinguish hierarchy, dependency, message order, and responsibility rather than reusing one arrow meaning for everything. Show branches needed to understand the claim without inventing a complete system. A diagram explains evidence; it is not execution evidence.

## Deliver and inspect

Honor the requested format. Use available format-specific capabilities when needed; do not require an extra plugin merely for style. Retain editable diagram source when diagrams are part of the deliverable. Choose layout, colors, headings, and density for this reader and medium; an accepted example establishes a quality reference, not a universal template.

Choose the available diagram tool for accurate meaning, reader clarity and total effort. Mermaid is sufficient for many simple relationships; an installed [optional Archify Skill](optional-archify.md) can supply reusable interactive HTML, node exploration and path tracing when useful. These are choices, not fixed complexity thresholds or required artifacts. The model may choose directly within the task; no new routing role or approval step is added. Tool checks do not verify professional claims or make an outdated diagram current.

Inspect the rendered artifact when creating a formatted document or diagram: readable labels, unambiguous connectors, no clipped or overlapping content, and usable navigation or source links. Check the claims and relationships as well as appearance. Report unavailable render checks honestly; do not replace them with an unobserved pass. Use review and stopping conditions proportional to the approved task; do not introduce a recurring review loop.

Provide enough provenance for a reader to inspect consequential claims without filling the main narrative with logs. Rendering checks, independent review, and actual reader feedback are different evidence; do not claim broad reliability from one accepted sample. Publishing or sending externally still follows the task's authorization.

## Optional lookup sources

These links are lookup aids, not mandatory dependencies or copied templates. The guidance above is original synthesis; no third-party artwork, font, or template is bundled. Check the source and license before importing assets.

- [Diátaxis](https://diataxis.fr/): choosing documentation around reader needs; do not force every deliverable into all four forms.
- [Mermaid sequence notation](https://mermaid.js.org/syntax/sequenceDiagram.html): participants, messages, and alternatives when this notation is chosen.
- [C4 notation](https://c4model.com/diagrams/notation): identifying scope, elements, and relationships when an architecture view helps.
