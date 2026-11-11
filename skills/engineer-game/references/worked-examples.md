# Worked engineering examples

All names, requirements and code contracts below are invented and engine-neutral. Facts mean facts within the stated fictional scenario. No run, review, measurement or successful implementation is claimed. Adapt the reasoning to inspected project evidence; do not copy these product decisions into another task. Each review handoff below describes material to route to an independent Reviewer, not a verdict or a substitute for dispatch. Follow the triggers and identity requirements in [working-method.md](working-method.md).

## 1. Overall requirement: reward settlement for a new level

**Requirement.** After a completed run, credit its configured reward once and show the resulting receipt. Leaving before completion earns nothing. Closing the receipt panel does not undo a completed settlement. Retrying the same run returns its original receipt. Only the account's authoritative writer may change its balance.

**Facts / unknowns.** The fictional `FinishRun` entry receives a run ID; `RunStore` owns completion state; `AccountWriter` owns balance writes; `ReceiptPanel` displays results. Inspect their real equivalents before accepting this shape. The crucial unknown is whether the writer can atomically store a receipt with the balance update. A separate “already paid” flag written afterwards could leave a duplicate-credit window on failure.

**Options and decision.** A: put calculation and credit in the panel's open callback; it is quick to wire but ties money changes to repeated presentation and loses a clear cancellation boundary. B: resolve completion and reward at the settlement boundary, commit through `AccountWriter`, and display the stored receipt. Choose B for the stated repeat/ownership requirement. It need not create several new modules: keep the tightly interacting commit together and extract only the reward rule if its variability warrants it. This applies [Cloudwu's data-interaction and change lens](https://blog.codingnow.com/2015/04/skynet_mmo.html), not his server topology.

**Before editing.** Record: “A run has no receipt until its authoritative completion is accepted; receipt plus balance credit must commit together under the run ID. Re-entry returns the stored receipt, including the originally calculated amount.” Probe the writer's failure behavior if its contract is unclear. If atomic storage is absent, either constrain an authorized disposable prototype to session-only credit or return the persistence gap for a scope decision; do not promise durable exactly-once settlement.

**Implementation tasks, in order.**
1. Trace completion and abandon into `RunStore`; define which transition wins if they race. Preserve the accepted completion if the user merely closes the panel.
2. Read the reward from trusted configuration, calculate from the accepted run result, and pass that result to the authoritative writer. Verify the caller's account/run relationship; reject an unrelated account before any write.
3. Implement lookup-or-commit by run ID at the writer's existing transaction boundary. Publish a receipt only after commit; distinguish a definite rejected write from an unknown commit outcome that requires lookup.
4. Wire `FinishRun` and the panel to the receipt result. A panel retry uses the same run ID and never directly credits the account.

**Finite validation.** Enter through normal completion: one credit and matching receipt. Abandon before completion: no receipt or credit. Repeat completion and reopen the panel: the same receipt and no additional credit. Cancel presentation after commit: credit remains. Supply another account's run: no write. Interrupt a commit response and retry: look up the receipt rather than assume failure or credit again. Run the writer's atomic-failure check; session-only prototype evidence cannot establish crash recovery.

**Next change.** If the approved project task includes a second reward configuration, exercise both level entries. Expected: configuration/calculation changes, while account ownership and retry logic stay shared. If duplicate commit code is needed, revisit the boundary. Otherwise record the expected edit scope as an untested prediction. This is a bounded production-repeatability check inspired by [Rami Ismail](https://ltpf.ramiismail.com/prototypes-and-vertical-slice/); it does not justify a universal reward framework.

**Actual review handoff.** Before implementing a new settlement boundary, route the requirement, completion/abandon flow, writer contract, commit decision and finite cases for technical review. At completion, route the actual balance-write callers, transaction/receipt implementation, panel path and raw repeated/failure results. Ask whether the implementation preserves ownership and atomicity; the design note alone cannot prove either. A second configuration is exercised only when authorized in the project task; otherwise its predicted edit scope remains untested.

## 2. New feature / optimization: short-lived sound emitters

**Requirement.** Play bursts of noncritical cosmetic sounds without exceeding the task's frame-time and memory budgets; level exit must stop playback and release level-held resources. Missing a cosmetic sound when the agreed concurrency limit is reached is acceptable in this fictional requirement. This says nothing about dialogue or essential gameplay cues.

**Facts / unknowns.** `PlayCosmetic` currently creates an emitter and releases it on completion. Emitters hold clip references, position, volume, pitch and a completion subscription. Allocation/initialization cost, typical concurrency and worst credible burst are unknown; “short-lived” alone does not establish that a pool helps.

**Options and decision.** A: retain create/release; this is simpler, carries no idle pool and may already meet budgets. B: reuse a bounded set; it may reduce repeated setup but retains memory and adds reset, capacity and stale-callback responsibilities. [Nystrom's Object Pool chapter](https://gameprogrammingpatterns.com/object-pool.html) makes those costs explicit. Prefer A until comparable measurements justify B; choose neither from pattern familiarity alone.

**Before editing.** Record the decision threshold using the actual task budget or declared baseline. Measure A with the same target/build, clip readiness, burst sequence, duration and concurrency as B; separate cold startup from warm playback. Capture allocation/setup time, frame-time spikes, peak active emitters, retained memory after quiet time and resources after exit. [Wube's optimization account](https://www.factorio.com/blog/post/fff-421) illustrates measuring under play-test loads; its results are not transferable numbers. If A meets the relevant budget and no material benefit is demonstrated, finish with A and the evidence.

**Implementation tasks if measurements select B.**
1. Give the existing audio owner a bounded emitter collection and an agreed exhaustion policy. Size from observed demand and memory limits; no silent unbounded growth. Prewarming, if used, belongs in measured loading cost.
2. Borrow through `PlayCosmetic`; initialize every playback field and associate completion with that borrow's identity. Do not expose a reusable raw emitter as a permanent caller-owned object.
3. Return exactly once on natural completion, explicit stop or failed start: remove the subscription, stop playback, clear clip/owner references and reset mutable state before making the slot available. Ignore a prior borrow's late completion.
4. On level exit, prevent new borrows, stop active playback and dispose the collection's resources. Preserve any separately owned shared audio cache according to its contract; a pool clear alone does not prove release.

**Finite validation.** Normal completion returns a slot; reuse with different volume/pitch/position does not inherit old values. Repeated stop and late completion do not double-return. A failed start leaves no active borrow. At capacity, the approved cosmetic-drop result is observable and memory remains bounded. Exit during playback leaves no level-held clips/subscriptions; reopening works. Repeat the same measured burst for A and B and report the actual tradeoff, even if B is rejected.

**Next change.** When an authorized content change introduces a longer cosmetic clip, return should follow actual completion, not an assumed timer; remeasure concurrency before changing capacity. Without that task, this remains a predicted extension check. A later requirement for never-dropped dialogue would invalidate the exhaustion policy and merits a new decision, not a hidden expansion of this pool.

**Actual review handoff.** A proposed change from create/release to shared reuse changes resource lifetime: route the measurements, capacity/exhaustion decision and borrow/return ownership before implementation. Final source review inspects real borrow/return sites, reset fields, stale completion guards and exit cleanup alongside the same-load measurements. Keeping create/release after inspection may be the correct result; a pool or more classes is not evidence of improvement.

## 3. Fix: a closed asynchronous preview receives an old result

**Requirement.** Selecting an item shows only that selection's preview. Closing the window promptly removes it; a late result must neither reopen the window nor retain its resource. Reopening starts a new window lifetime. A failed current request shows an error and permits retry.

**Facts / unknowns.** Trace `SelectItem -> PreviewController -> PreviewLoader -> decode/load -> completion -> view`, then `Close -> controller cleanup`. In this fictional dependency contract, cancellation requests may race with completion; each successful load returns a resource lease that the recipient must release. Callback delivery and release semantics still need inspection in an actual task. A boolean `isOpen` alone cannot distinguish a closed-and-reopened window from its predecessor.

**Options and decision.** A: request cancellation and trust that callbacks stop; this is sufficient only if the dependency guarantees both no later delivery and cleanup of any result. B: request cancellation for wasted-work reduction, and also check window/request identity before applying a result, releasing a rejected result. Select B for the stated contract. Keep the guard in the controller that owns selection/lifetime; do not teach the loader about widgets or add a global preview manager.

**Before editing.** Record: “Only the current request in the current open-window lifetime can transfer its lease to the displayed preview. Every other successful result is released once.” Reproduce close-before-completion with a controllable delay. Probe cancel-versus-complete only if dependency inspection cannot establish the contract; this is an uncertainty-reduction use of [Cerny and John's prototype principle](https://media.gdcvault.com/GD_Mag_Archives/GDM_June_2002.pdf), not a reason to build a new loader framework.

**Implementation tasks, in order.**
1. Establish the actual loader contract: cancellation behavior, callback execution context, success lease owner and error cleanup. Keep the required view-thread dispatch, and evaluate identity when applying the completion there.
2. In the controller, invalidate the previous request identity before starting a new selection; cancel its work as supported. Capture an immutable window/request identity in the completion path.
3. Apply only a current result. Transfer its lease to the view owner and release the replaced lease; release stale successful results without touching current UI. Route only a current failure to the error state; stale errors must not clear a newer preview.
4. On close, invalidate the window lifetime first, cancel pending work, detach input/listeners and release the displayed lease. Handle failed start or partial creation according to the inspected dependency contract, including any resource created before failure.

**Finite validation.** Normal selection displays and retains exactly its lease. Close before success: nothing reopens and the late lease is released. Close, reopen, then deliver the old response: new content stays intact. Select A then B and complete A last: B stays visible and A is released. Fail the current request: error permits a successful retry; fail an old request: current content stays. Repeat close: no double release. Drive these from the actual window/controller entry, plus the smallest controllable dependency seam needed to schedule responses.

**Next change.** Exercise a second selection while the same window remains open; the request identity should handle it without duplicating window-lifetime logic. If later adding a shared preview cache, revisit lease ownership explicitly: discarding a view result must release its lease, not destroy another view's cached resource.

**Actual review handoff.** For the changed asynchronous lifetime, route the inspected cancellation/lease contract and current-versus-stale decision for technical review. Final source review follows every successful-result branch to transfer or release, then checks close/reopen and reordered-completion evidence through the actual controller entry. A null check or cancelled flag does not by itself establish that stale resources are released. These are proposed review questions; no reviewer outcome is prefilled.
