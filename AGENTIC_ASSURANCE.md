# OpenDevs Agentic Assurance

> **Upstream:** `MosslandOpenDevs/agentic-assurance-profile`, pinned in [`.agentic-assurance/adoption.yaml`](.agentic-assurance/adoption.yaml).
>
> **Purpose:** Connect this repository (`links.moss.land`) to the shared OpenDevs assurance profile without duplicating the upstream standard locally.
>
> **Status:** The PROFILE.md §4.3 intent review is **complete as of 2026-07-18** — purpose and non-goals, critical claims and invariants, the behaviour classification, and the residual register were all reviewed and decided by the repository owner (recorded in `.agentic-assurance/adoption.yaml` `human_review`). Private vulnerability reporting is enabled and verified (`EV-INTAKE-001`). See §12 for the completion-criteria table.

Before any material change, read:

1. `AGENTIC_ASSURANCE.md`;
2. `.agentic-assurance/adoption.yaml`;
3. the project system specification and non-goals (`assurance/SYSTEM.md`);
4. affected claims, invariants, defeaters, and residuals (`assurance/*.yaml`);
5. the active change specification (the pull request / issue).

---

## 1. Adoption declaration

This repository adopts the **OpenDevs Agentic Assurance Profile** for software produced or maintained substantially by AI agents.

The profile complements—not replaces—the repository's existing mechanisms:

- `AGENTS.md` for persistent agent instructions;
- the GitHub pull-request change workflow documented in `README.md`;
- the pure, dependency-free generator (`build/generate.mjs`) and AWS Amplify deployment;
- `customHttp.yml` response-header controls and the registry JSON Schema.

The working chain is:

```text
Intent → Claims → Invariants → Enforcement → Evidence → Residuals
```

The pinned upstream profile defines the terms and generic obligations. This file defines how this repository adopts and applies them. The project's as-built reconstruction is in [`assurance/SYSTEM.md`](assurance/SYSTEM.md).

---

## 2. Pinned upstream profile

The declaration lives in [`.agentic-assurance/adoption.yaml`](.agentic-assurance/adoption.yaml) — **the pin's only home**. Read `upstream.version` and `upstream.commit` there; this document deliberately does not restate the values. (This file used to carry a copy of the pin; it went stale across two re-pins because re-pin changes touch `adoption.yaml` and the workflow, not prose, and the validator does not read markdown. The upstream profile's template now instructs exactly this — keep concrete pin values out of prose.)

```yaml
upstream:
  repository: MosslandOpenDevs/agentic-assurance-profile
  # version + commit: see .agentic-assurance/adoption.yaml — not restated here

project:
  name: Mossland Verified Links
  repository: MosslandOpenDevs/links
  human_owner: MosslandOpenDevs maintainers (Mossland)

profiles:
  - core
  - service
  - trust-critical
  - data-curation
```

The full commit SHA is the normative pin. A branch such as `main` MUST NOT be the sole reference. Agents MUST NOT update the pin silently; an upstream upgrade requires a dedicated change with impact analysis and a matching update to the `@`-ref in `.github/workflows/assurance.yml`.

---

## 3. Authority and precedence

When sources disagree, use this order:

1. human-approved project intent and non-goals;
2. the pinned upstream assurance profile;
3. human-approved local claims, invariants, decisions, and residual acceptances;
4. the active change specification (the pull request / issue);
5. implementation and generated output as evidence of current behavior—not automatic proof of intended behavior.

Current production behavior is not a specification by itself. An agent MUST report conflicts among intent, profile obligations, local artifacts, code, and observed behavior. It MUST NOT silently rewrite one to match another.

Only the named human owner or governing body (see the adoption file; ecosystem-registry contents are ultimately governed by Mossland DAO via Agora) may approve product intent and non-goals, critical invariants, public claim wording and limitations, weakening of a critical control, or acceptance of a critical residual.

---

## 4. Local artifacts

```text
AGENTS.md
AGENTIC_ASSURANCE.md
SECURITY.md
.agentic-assurance/adoption.yaml
assurance/
├── SYSTEM.md
├── INVARIANTS.yaml
├── CLAIMS.yaml
├── DEFEATERS.yaml
├── RESIDUALS.yaml
└── THREAT_MODEL.md
```

Do not copy the complete upstream profile into this repository; local duplication creates an untracked fork and future semantic drift.

---

## 5. Profile selection

Adopted, confirmed by the owner on 2026-07-18: `core`, `service`, `trust-critical`, `data-curation`.

- `core` — the repository is substantially AI-agent-built.
- `service` — a deployed website plus a public read-only registry endpoint (AWS Amplify).
- `trust-critical` — domain authenticity / anti-phishing is the page's core purpose.
- `data-curation` — the registry is curated, classified, scored data (tier/chip/status judgements, and the `stampClass` significance weighting consumed by Passport). Added by owner decision 2026-07-18. This is an established upstream profile, promoted from provisional in v0.2.0 (see PROFILE.md §5) after a public adopter exercised every §6.4 obligation; under v0.4.0 only `agent-runtime` remains provisional, so the validator emits no provisional warning on its selection. Its PROFILE.md §6.4 considerations are recorded openly: `RES-CURATION-001` (external fact vs editorial judgement not structurally separated) remains ACCEPTED, and `RES-CURATION-002` (versioned classification/scoring rubric) is RESOLVED; see `assurance/SYSTEM.md` §3.1.

---

## 6. Adoption workflow

Initial adoption is a repository-archaeology task, not a feature task. Discover and reuse existing mechanisms before creating anything; reconstruct the as-built system read-only (recorded in `assurance/SYSTEM.md`); classify every material conclusion as `VERIFIED`/`INFERRED`/`UNKNOWN`/`CONTRADICTED` with concrete evidence; then obtain human intent review (§6.3 of the pinned profile) before broad remediation; and remediate in scoped, reviewable changes.

---

## 7. Material change workflow

A material change affects externally visible behavior, the registry's meaning, public claims, the security headers, Passport eligibility, or critical dependencies. Before implementation, the pull request (see `.github/PULL_REQUEST_TEMPLATE.md`) states intent and non-goals, affected claims/invariants, before/after behavior, failure and abuse cases, required deterministic evidence, and expected residual impact. Reuse the existing GitHub PR workflow; do not duplicate it.

---

## 8. Evidence and residual rules

- **Tests verify; controls enforce.** A critical invariant should have both.
- "All checks passed" is not evidence unless the underlying results are linked and reproducible; bind evidence to a commit SHA, artifact digest, or deployment identifier.
- A **defeater** is a concrete reason a claim may be false; a **residual** is a known limitation or remaining doubt. Residuals are expected; hidden residuals are not. Do not close a residual merely because no recent failure was observed.
- For security-sensitive work: audit read-only, record findings, remediate separately, re-verify independently. The same agent context must not be sole author, implementer, auditor, and final judge of a critical change.

---

## 9. Public disclosure and issue tracking

Assurance artifacts here are a sanitized public view, not a complete private security record. This repository MUST NOT publish secrets, personal data, or actionable details of an unpatched vulnerability. Suspected exploitable findings go through GitHub Private Vulnerability Reporting (see `SECURITY.md`), not a public Issue.

Claims, invariants, defeaters, and residuals use stable semantic IDs (`CLAIM-`, `INV-`, `DEF-`, `RES-`) independent of GitHub Issue numbers; Issues and pull requests should reference affected IDs. Closing an Issue or merging code does not by itself resolve an assurance item.

---

## 10. Prohibited agent behavior

An agent MUST NOT redefine intent without approval; label behavior `INTENDED` merely because it exists; weaken or skip a check to obtain a green result; fabricate evidence or citations; hide unknowns; silently upgrade the upstream pin; fork the upstream profile locally; publish restricted material; or accept a critical residual on the owner's behalf. When certainty is unavailable, record `UNKNOWN`, a defeater, or a residual.

---

## 11. Root `AGENTS.md` integration

The normative "OpenDevs Agentic Assurance" reading-order section is reproduced at the top of [`AGENTS.md`](AGENTS.md). If the two ever differ, this file governs.

---

## 12. Adoption completion

This adoption is **not** complete merely because these documents exist. Status against the pinned profile's completion criteria:

| Criterion | State |
|---|---|
| Upstream pin resolves to a real version and commit | ✅ pinned in `.agentic-assurance/adoption.yaml`; tag-commit agreement and caller @-ref agreement checked in CI |
| Human-approved purpose and non-goals recorded | ✅ owner review 2026-07-18 (`assurance/SYSTEM.md` §2) |
| Critical claims and invariants stated, with enforcement/evidence or explicit `UNKNOWN` | ✅ 7 invariants, 5 claims; `intent.authority` set on each |
| Residual register active and owned | ✅ 8 residuals — 3 RESOLVED, 4 ACCEPTED with rationale, 1 OPEN |
| Material-change workflow references the assurance artifacts | ✅ `.github/PULL_REQUEST_TEMPLATE.md` |
| Private vulnerability reporting (required for a public `trust-critical` adopter, PROFILE.md §6.3) | ✅ enabled 2026-07-18, verified by API (`EV-INTAKE-001`) |

All six criteria are met, so the owner **may** describe this bounded revision as conforming to the pinned profile (PROFILE.md §17). That remains the owner's statement to make, not the drafting agent's.

One residual stays deliberately open — `RES-PROVENANCE-001` (prose-grounded evidence). It is not critical-impact, so it does not block §17, but it remains open and owned rather than being closed for tidiness. (`RES-CURATION-002`, the versioned-rubric gap, was deliberately not accepted in the review and instead remediated the same day — RESOLVED.)

Conformance means the project's promises, controls, evidence, counterarguments, and remaining uncertainty are represented according to the pinned profile. It does **not** mean this system is secure or bug-free.
