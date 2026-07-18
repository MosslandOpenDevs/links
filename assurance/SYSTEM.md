# As-built system description — links.moss.land

> **Status:** As-built reconstruction produced during Agentic Assurance Profile adoption. The purpose, non-goals (§2) and behavior classifications (§9) were **reviewed and approved by the human owner on 2026-07-18** (PROFILE.md §4.3). They are now approved intent: an agent must not redefine them without a new owner decision, and each invariant's `intent.authority` points at this review.
>
> **Evidence rule:** Non-`UNKNOWN` conclusions cite concrete evidence (file:line, header, command output). An AI narrative is not evidence by itself.

---

## 1. Purpose and users

**Mossland Verified Links** (`https://links.moss.land`) is the canonical, KR-primary bilingual registry of official Mossland domains, ecosystem apps, developer resources, and third-party market references. Its core job is **anti-phishing**: telling a visitor which domains are genuinely Mossland's, so that "anything not listed here should be treated as unofficial" (`README.md:3-11`).

Users: (a) end users checking whether a Mossland address is genuine; (b) other Mossland properties (moss.land, Passport, City, WA) that fetch the registry cross-origin to verify domains and drive Passport ecosystem stamps (`README.md:13-21`); (c) search engines and AI agents consuming `llms.txt` / the JSON registry.

It is a static site deployed on AWS Amplify (`amplify.yml`, `README.md:8`).

## 2. Non-goals

Reconstructed from the code and copy, and **confirmed by the owner on 2026-07-18**. These are human-approved intent: an agent must not redefine them (PROFILE.md §15), and a change to any of them is a material change requiring its own review.

- **Not a general CMS** — the rendered files are generated, never hand-edited (`README.md:23-32`). Machine-enforced, not merely documented: the generator renders solely from `reg.services`, and `.github/workflows/registry.yml` fails the build when committed output diverges from a fresh run. This is the structural precondition for `INV-REG-001`, and therefore for the anti-phishing claim `CLAIM-PHISH-001` — a hand-editable page could show links the registry does not contain, and the registry would stop being the source of truth that Passport and other properties verify against.
- **Not a price feed, trading venue, or investment advice** — third-party market links are "reference only and are not trading recommendations" (`build/generate.mjs:31`, visible in the rendered output). Adding a price widget or chart would require revisiting this non-goal first.
- **Not a Passport-eligibility grantor for third parties** — market and off-domain channel links are `passportEligible: false` by contract (`ecosystem-registry.schema.json:102-111`), enforced in CI since 2026-07-18. No exchange or off-domain channel can ever back an ecosystem stamp.
- **Not a live uptime monitor** — service `status` reflects point-in-time manual verification, not continuous monitoring. Consumers must not read `status` as a real-time signal. This non-goal is the basis on which `RES-STATUS-DRIFT-001` was accepted. Evidence note: unlike the other three, this one is inferred from an absence (no monitoring exists) rather than from a positive artifact, so it rests on the owner's confirmation rather than on a machine-checkable control.

## 3. Domain entities and identifiers

- **Registry document** — `ecosystem-registry.json`, the single source of truth (`version` 1.0.0, `generatedAt` 2026-07-06). Authoritative at `https://links.moss.land/ecosystem-registry.json`.
- **Service** — one entry in `services[]`. Stable identifier: `id` (pattern `^[a-z0-9-]+$`, `ecosystem-registry.schema.json:50`). Key fields: `domain`, `url`, `tier`, `status`, `section`, `owner`, `passportEligible`, `stampType`, `stampClass`, `labelKo`/`label`, `chip`, `artifact`, `hidden` (`ecosystem-registry.schema.json:45-101`).
- **Schema contract** — `ecosystem-registry.schema.json` (JSON Schema draft 2020-12), authoritative at `https://links.moss.land/ecosystem-registry.schema.json`.
- **Passport stamp identity** — `stampType` (namespaced id, e.g. `identity_holder`) and `stampClass` (significance tier: core/governance/participation/connect/lab/showcase), consumed by Passport.

### 3.1 External fact vs editorial judgement (`data-curation`)

The `data-curation` profile requires separating externally sourced facts from local editorial judgement (PROFILE.md §6.4). The registry does **not** yet encode that split structurally; this narrative list is the interim separation, and closing it properly is tracked as `RES-CURATION-001`.

| Kind | Fields |
|---|---|
| **Externally observed fact** | `domain`, `url`, `ticker`, `runtime.domain`/`runtime.url` |
| **Mossland editorial judgement** | `tier`, `chip`, `status`, `label`/`labelKo`, `section`, `featured`, `note`, `passportEligible`, `stampType`, `stampClass` |
| **Provenance / bookkeeping** | `id`, `owner`, `hidden`, `artifact`, `sourceOfTruth`, `lastDataAt`, document-level `version` / `generatedAt` |

Two properties of this table matter for consumers:

- **`stampClass` is a scoring rubric, not a fact.** It weights Passport stamps ("so stamps can be weighted rather than treated as a flat attendance log", `ecosystem-registry.schema.json:78-79`), and Passport consumes it. The rubric itself is unversioned — `RES-CURATION-002`.
- **Provenance is thin on the fact side.** `sourceOfTruth` is set on only a few entries and `lastDataAt` is `null` on every entry, so an observed fact carries no capture time. Also `RES-CURATION-001`.

## 4. State transitions

- **Registry → generated artifacts.** `node build/generate.mjs` reads the registry and writes `index.html`, `embed.html`, `llms.txt`, `sitemap.xml` (`build/generate.mjs:347-350`). Idempotent; committed output equals a fresh run (`amplify.yml:7-8`). Trigger: a human editing the registry and running the generator, then committing both (`README.md:103-108`).
- **Commit → deploy.** Push to `main` triggers AWS Amplify, which runs the generator (`node build/generate.mjs || true`) and publishes the artifact list (`amplify.yml:5-22`).
- **Service `status`** — one of `operational|degraded|beta|paused|offline|deprecated` (`ecosystem-registry.schema.json:41-44`), changed by human curation after live verification.
- **`chip` lifecycle** — an empty-but-live service carries an explicit `chip: "실험"` until it has real data, then the field is removed and it falls through to its tier chip (`README.md:95-97`, `ecosystem-registry.json` `media`).

## 5. Trust boundaries and external dependencies

- **Human curation → registry.** The strongest trust boundary: `owner`/`domain`/`passportEligible` are hand-set. Authenticity rests here (`INV-PHISH-001`, `DEF-PHISH-001`).
- **Registry → cross-origin consumers.** Served with `Access-Control-Allow-Origin: *` (public, read-only, non-credentialed) — `customHttp.yml:35-50`. Consumers trust the registry's authenticity judgement.
- **AWS Amplify.** Hosts the site and applies `customHttp.yml` response headers (CSP, HSTS, CORS, frame-ancestors). Security headers depend on Amplify honouring this file (`DEF-HTTP-001`).
- **Governance of registry contents.** Per the registry's own `agora` entry and `llms.txt` notes, Mossland DAO treats an Agora (`agora.moss.land`) result as its binding decision of record (`build/generate.mjs:329`, `ecosystem-registry.json` `agora.note`). Agora is therefore the ultimate governing body for what the ecosystem officially includes.
- **Third-party targets.** Market/exchange domains (Upbit, Bithumb, CoinMarketCap, …) are external, unverified, and explicitly labelled 제3자 (`INV-MARKET-001`).
- See `assurance/THREAT_MODEL.md` for the adversarial view.

## 6. Public claims and user-visible promises

Material public claims are registered with stable IDs in `assurance/CLAIMS.yaml`:

- `CLAIM-PHISH-001` — "apart from third-party market links, every link here is either an official Mossland domain or an official account Mossland operates; unlisted ⇒ treat as unofficial" (`build/generate.mjs:191-194`; wording refined 2026-07-18 so the public claim no longer over-states control of off-domain platforms).
- `CLAIM-REG-001` — the JSON registry is the single, cross-origin-fetchable source of truth; the page is a deterministic projection.
- `CLAIM-PASSPORT-001` — third-party and off-domain channel entries are never Passport-eligible (schema-verifiable); `CLAIM-PASSPORT-002` — only Mossland-controlled domains/accounts back a stamp (curation-attested).
- `CLAIM-MARKET-001` — third-party market links are reference only, not recommendations.

## 7. Enforcement inventory

- **Chip derivation** — `build/generate.mjs chipFor()` (`:45-53`) drives the 제3자 vs verified-Mossland trust signal from `owner`/`tier`. Backs `INV-PHISH-001`, `INV-MARKET-001`.
- **Registry schema `allOf`** — forces `passportEligible: false` for `third_party` and `channel` tiers (`ecosystem-registry.schema.json:102-111`). Backs `INV-PASSPORT-001`.
- **CI registry gate** — `.github/workflows/registry.yml` runs `.github/scripts/validate-registry.py` (schema validation + "every Passport-eligible entry is owner `mossland`" + unique ids) and a regenerate-and-diff step, on every push and pull request. Backs `INV-PASSPORT-001` and `INV-REG-001`; added 2026-07-18, closing `RES-CI-VALIDATION-001`.
- **HTML escaping** — `esc()` on every `card`/`domLine`/section-title interpolation (`build/generate.mjs:12-13`); the schema-constrained `generatedAt` date in the footer/sitemap is rendered directly (bounded exception). Backs `INV-RENDER-001`.
- **CSP / HSTS / CORS scoping / frame-ancestors** — `customHttp.yml:1-50`; the overall HTTP-header posture. Backs `INV-CORS-001`, `INV-FRAME-001`.
- **Generator as single writer** — pages rendered only from `reg.services`; README forbids hand edits. Backs `INV-REG-001`.

## 8. Verification and evidence inventory

- **Idempotent regeneration** — `node build/generate.mjs && git diff --exit-code` reproduces committed output (evidence bound to a commit). This is the primary reproducible check today.
- **JSON Schema validation** — `ecosystem-registry.json` can be validated against `ecosystem-registry.schema.json` by any consumer; **not yet wired into CI** (`RES-CI-VALIDATION-001`).
- **Manual live-site verification** — descriptions/statuses grounded in the live services, recorded via the footer "최종 확인" date (`build/generate.mjs:180`).
- **Bound evidence records** — `assurance/evidence/EVIDENCE.md`: `EV-PROJECTION-001` (regenerate-and-diff proves the committed pages are a pure projection; re-captured on each generator/registry change, latest `7dbfc80`) and `EV-HEADERS-001` (live capture proves the deployed CSP/HSTS/CORS/frame-ancestors match `customHttp.yml`).
- **Continuous validation** — two workflows run on every push and pull request: `.github/workflows/assurance.yml` (the pinned upstream profile validator) and `.github/workflows/registry.yml` (registry schema contract + projection diff). The registry gate was verified by a negative test before merge: marking a `third_party` entry `passportEligible` failed the build with two errors.
- **Remaining gap:** there is still no unit-test suite, and no *continuous* deployed-header assertion — the headers were confirmed by a one-time live capture and that residual was accepted (`RES-HEADERS-001`, ACCEPTED 2026-07-18) rather than remediated, because a live-site check in CI would make the build network-dependent.

## 9. Behavior classification

**All rows below were reviewed and approved by the human owner on 2026-07-18.** Five rest on machine-checkable evidence (schema constraint, served headers, command output, code behaviour), one on generator code logic, and three on prose — the prose-grounded ones remain tracked by `RES-PROVENANCE-001` for later re-grounding, approval notwithstanding.

| Behavior | Classification | Evidence | Conclusion |
|---|---|---|---|
| Non-third-party listings render as verified Mossland; page states unlisted ⇒ unofficial | INTENDED | `build/generate.mjs:45-53, 191-194` | INFERRED |
| Official off-domain channels/accounts (Medium, X, GitHub; owner mossland) render the 공식 chip, not 제3자 | INTENDED | `build/generate.mjs:45-53`; README chips table ('Verified Mossland domain or official channel') | VERIFIED |
| Rendered pages are a pure projection of the registry | INTENDED | `EV-PROJECTION-001`; `build/generate.mjs:76-97` | VERIFIED (at latest capture) |
| Registry JSON served cross-origin with `ACAO: *` (public, read-only) | INTENDED | `customHttp.yml:35-42` | VERIFIED |
| `passportEligible:false` enforced for third_party/channel in schema | INTENDED | `ecosystem-registry.schema.json:102-111` | VERIFIED |
| `media` shows explicit 실험 chip while empty | INTENDED | `ecosystem-registry.json` media `chip:"실험"`; `README.md:95-97` | VERIFIED |
| `alpha` paused / `ao` degraded recorded as of 2026-07-06 | INTENDED (point-in-time data) | `ecosystem-registry.json` notes | VERIFIED (as of that date) |
| Amplify runs generator with `\|\| true`, shipping committed files even on generator failure | INTENDED (resilience) — owner-confirmed 2026-07-18 [^amplify] | Owner confirmation recorded in `.agentic-assurance/adoption.yaml` `human_review` | VERIFIED |
| JSON-LD blocks not escaped against script-element termination | ACCIDENTAL — **remediated 2026-07-18** | `build/generate.mjs` jsonLd() now escapes `<`; `RES-RENDER-JSONLD-001` RESOLVED | VERIFIED |
| No CI validation of registry against its schema | ACCIDENTAL — **remediated 2026-07-18** | `.github/workflows/registry.yml`; `RES-CI-VALIDATION-001` RESOLVED | VERIFIED |

Current production behavior is evidence of current behavior, not automatic proof of intended behavior.

**Evidence provenance caveat.** Rows above grounded in machine-checkable artifacts — schema constraints, served response headers, command output, code behaviour — are solid. Rows grounded in *prose* (code comments, README descriptions, registry `note` fields) are weaker, because this repository's prose was largely written in AI-co-authored commits and PROFILE.md §7 excludes AI-generated explanation as evidence by itself. Tracked as `RES-PROVENANCE-001`.

[^amplify]: **Why the code comment is not cited as the evidence here.** `amplify.yml:6-8` states the rationale ("`|| true` keeps the deploy from breaking if the generator ever fails"), and the first draft of this table cited it. But `git blame` puts those lines in `d688deb`, a commit carrying `Co-Authored-By: Claude Opus 4.8` — so the rationale is plausibly AI-authored, and PROFILE.md §7 is explicit that *an AI-generated explanation is not evidence by itself*. Citing it would have been circular: one agent asserts intent in a comment, another agent cites that assertion as proof of human intent — exactly what §15 forbids. The classification was therefore re-grounded on an explicit owner confirmation. Note the design is coherent now that `.github/workflows/registry.yml` verifies the committed output at merge time: what Amplify ships on generator failure is known-good, already-validated output. The bounded side effect the owner accepted is that a generator failure on Amplify is silent in the deploy log.

## 10. Known unknowns

- Whether "unlisted ⇒ unofficial" is intended as a strong guarantee or a best-effort heuristic — resolved by the §4.3 intent review. Tracked as a limitation on `CLAIM-PHISH-001`.
- ~~Whether the omission of registry-schema CI validation is deliberate scope or simply unbuilt~~ — settled 2026-07-18: classified ACCIDENTAL and remediated (`RES-CI-VALIDATION-001` RESOLVED).
- How much of this repository's prose-based evidence actually reflects human intent rather than agent narrative — `RES-PROVENANCE-001`. Resolved per row by re-grounding on a machine-checkable artifact or an explicit owner confirmation.
- What the intended semantics of the tier/chip/`stampClass` rubric are over time — there is no rubric version history, so past classifications cannot be interpreted against the rubric that produced them (`RES-CURATION-002`).
- ~~Whether `data-curation` should be added~~ — decided 2026-07-18: added, with its PROFILE.md §6.4 gaps recorded as `RES-CURATION-001` and `RES-CURATION-002`.
- ~~Whether a specific named person should be the recorded `human_owner`~~ — decided 2026-07-18: authority rests with the MosslandOpenDevs maintainers as a body.
