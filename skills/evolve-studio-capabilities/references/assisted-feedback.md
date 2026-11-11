# Assisted Preview feedback

The member speaks naturally; the Agent prepares the record. Use an Issue for a problem or suggestion. Use a PR only when there is an actual authorized change to review. The member need not know either term.

## Prepare from the conversation

1. Recover the task, observed problem, intended result, and reliably known version. Ask only for missing information that changes the report's meaning or destination. Unknown version/reproduction details do not block feedback.
2. Summarize into a short title and a minimal abstract report. Exclude game names/design/code/status, private assets, credentials, personal paths and unrelated conversation. Keep original project evidence in the game project; only include approved shareable excerpts or an authorized evidence reference. Do not attach the whole conversation or repository. Do not invent reproduction results or claim the helper redacts sensitive content.
3. Use the [AGDS Preview repository](https://github.com/baizixn/agds-preview) and its [Issues](https://github.com/baizixn/agds-preview/issues) for AGDS feedback. Use the game project repository for game fixes. If the authorized task names a different destination, resolve that destination before submitting.
4. For repeat requests, look for a previously prepared packet or confirmed Issue URL in the current task. Reuse it; add new evidence to the existing Issue only when authorized. Searching a remote for duplicates is useful when available, but unavailable search does not block a local draft.
5. Show the exact destination, title and body in plain language. “帮我反馈” authorizes preparation; it does not silently publish newly assembled private material. Ask to send only if the shown content/destination are not already covered by explicit authorization. Reuse existing authorization for unchanged content and scope.

## Optional local helper

When Python 3.11+ is available, the Agent may write curated UTF-8 JSON and run the bundled helper. The member does not run commands or configure tokens. With no Python, produce the same Markdown draft directly.

```json
{
  "observed": "交付后没有说明怎样打开成果。",
  "expected": "提供打开入口，以及实际验证过什么。",
  "context": "使用 AGDS 完成一个小任务。",
  "version": "未确认",
  "reproduction": "目前只有一次观察，尚未独立复现。"
}
```

`observed` is required; `title`, `context`, `expected`, `version`, and `reproduction` are optional strings. The Agent authors the JSON from already shareable material. Use a new output directory under the current task's allowed local records, outside the shared plugin source. Do not put game feedback in the AGDS repository.

```text
python -X utf8 <this-skill>/scripts/prepare_feedback.py --input <curated.json> --output-dir <new-feedback-directory> --repo-url https://github.com/baizixn/agds-preview
```

Omit `--repo-url` for file-only preparation. The helper writes `feedback.md`, `packet.json` and, when a destination is present, `issue-url.txt`. It accesses no network, credentials, Git state or project files beyond the explicit input. Status is always `prepared`, never `submitted`. The packet digest identifies draft bytes only, not a capability signal/proposal ID.

For a short report, the Issue URL contains encoded title/body. Do not open it before send authorization: even opening a prefilled URL sends its content to the server. Reports exceeding the conservative 1,800-character URL limit receive a plain form URL; copy the complete title/body from the packet into the form. No text is truncated. Same-input repeat preserves the output; conflicting or incomplete output is refused, requiring a different directory or manual inspection, never automatic deletion.

## Submit with existing tools

- After authorization, use an available GitHub connector or the browser's authenticated GitHub Issue form. Respect the user's selected browser. Do not request a password or token in chat.
- If login is needed, let the member sign in through the normal browser. If access, browser control or network remains unavailable, hand over `feedback.md` with “尚未提交；将此文件转交维护者即可”. Do not claim an automatic background retry or upload.
- Fill the reviewed content and submit within the authorized scope. Verify the created Issue's canonical URL, title/body and repository before reporting success. Record that confirmed URL and status in the current task's local records. If the click/API response is uncertain, inspect the resulting page or search for that exact report first. If unresolved, report “提交结果待确认” and stop rather than sending a duplicate.
- Do not treat opening a form, a generated link, a screenshot of a draft, or a helper exit code as submission evidence. If the user chooses to submit manually, report a prepared draft until the resulting Issue is independently observed or supplied, with the evidence source stated.

## Assist an actual contribution

When a member asks “把这次修复提交到线上” after solving and testing a problem, treat this as authorization to submit the identified fix to the established review destination, including its required branch, commit, push and PR steps. Do not make the member restate known details or reconfirm these steps. If the destination or file scope is materially ambiguous, prepare everything else and ask only about that ambiguity. A request to prepare a draft alone does not authorize sending it.

Recover these from the conversation and actual files, rather than asking the member to fill a form:

- Original symptom, expected behavior, and a minimal shareable reproduction.
- What changed and why, with the actual selected files/diff; distinguish implemented changes from suggestions.
- Which checks actually ran, their results and relevant raw evidence; list failures, skipped and Not Run checks honestly. Contributor self-tests are not independent review.
- Starting version, current limitations/regression risk, and how the change could be reverted.
- What the maintainer needs to review or verify, linked to the resulting commit and PR.

Before Git changes, confirm the authoritative working copy, HEAD, dirty paths and allowed files. Determine whether the fix belongs to the game project or shared AGDS; do not upload game code/evidence to AGDS. Keep the underlying capability evolution's qualification, single owner, validation and review rules. A pending review need not prevent submitting a clearly marked Candidate PR; required review still gates adoption. If no implementation exists, prepare an Issue instead of manufacturing an empty PR.

Use a separate `codex/` branch. Inspect the selected diff and any proposed attachments; stage only the authorized files, including needed source/test files but excluding unrelated changes and credentials. Preserve existing staged work; when it is mixed, use an isolated worktree after the standard root/HEAD preflight, and copy only the authorized changes. Never use blanket staging to collect unknown project files. Match collected artifacts to the checks that produced them; rerun only checks invalidated by later changes or still required by the task. Prepare the PR body with the facts above.

Show a short submission summary (repository/base branch, selected files, checks and limitations), then proceed within the existing authorization. Use Git to commit/push and an available tool for the hosting service or authenticated browser to create the PR. Verify the remote branch/commit and resulting PR's repository, base/head and diff before returning its URL. Pushing a branch is not proof that a PR exists: if PR creation is unavailable, report the pushed branch/commit and “PR 尚未创建”. If a response is ambiguous, reconcile remote state before retrying. Without write access, hand the description and an inspected patch/artifact bundle containing the selected actual files to the maintainer, clearly marked not uploaded. Do not collect an entire project by default.

The AGDS Owner reviews and validates incoming Candidates, chooses which to adopt, then authorizes a combined release. PR creation is not merging, adoption or release; no default push to main, version change, or installation follows from submission.
