# Evidence records

Reproducible evidence bound to a revision or deployment, referenced by stable IDs
from the assurance registers (PROFILE.md §11 of the pinned upstream profile).
Each record states how to reproduce it and what it supports. An AI narrative is
not evidence; the commands and their observed output are.

**Record IDs are stable; the captures they hold are dated and bound to a revision.**
When an affected claim, control, dependency, or environment changes, re-run the
command and append a new capture rather than minting a new ID — that keeps the
register's references from going stale on every commit.

---

## EV-PROJECTION-001 — the committed pages are a pure projection of the registry

- **Command:**
  ```sh
  node build/generate.mjs && git diff --quiet && echo CLEAN
  ```
- **Supports:** `INV-REG-001` (pure projection); `CLAIM-REG-001`.
- **Does not close:** `DEF-REG-001` / `RES-CI-VALIDATION-001` — nothing in CI enforces this on every future commit. Each capture below proves the property at one revision only.

| Captured | Revision | Result |
|---|---|---|
| 2026-07-18 | `7dbfc80` (after the public-claim wording refinement) | `CLEAN` — committed output byte-identical to a fresh generator run |
| 2026-07-18 | `b53be92` (adoption baseline) | `CLEAN` — generator reported "28 visible links across 5 sections" |

---

## EV-HEADERS-001 — deployed responses carry the declared security headers

- **Command:**
  ```sh
  curl -sSI https://links.moss.land/
  curl -sSI https://links.moss.land/ecosystem-registry.json
  ```
- **Supports:** `INV-CORS-001` (CORS scoped to the read-only registry), `INV-FRAME-001` (framing restricted to Mossland origins).
- **Does not close:** `RES-HEADERS-001` — these are manual point-in-time captures, not an automated/continuous regression check.

### Capture 2026-07-18 (live deployment)

- `GET /` → `HTTP/2 200`
  - `content-security-policy: default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; form-action 'none'; frame-ancestors 'self' https://wa.moss.land https://*.wa.moss.land; upgrade-insecure-requests`
  - `strict-transport-security: max-age=63072000; includeSubDomains`
  - `x-content-type-options: nosniff`
  - `referrer-policy: strict-origin-when-cross-origin`
  - `cross-origin-opener-policy: same-origin-allow-popups`
  - `permissions-policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()`
- `GET /ecosystem-registry.json` → `HTTP/2 200`
  - `access-control-allow-origin: *`
  - `cross-origin-resource-policy: cross-origin`
  - `cache-control: public, max-age=300`
  - `content-type: application/json`

**Result:** the served responses match `customHttp.yml` exactly, including the scoped CORS `*` on the registry and the `frame-ancestors` allow-list.

---

## EV-INTAKE-001 — private security intake is live

Evidence for the `trust-critical` obligation that a public adopter has private vulnerability reporting (PROFILE.md §6.3, and the prerequisite in `docs/ADOPTION.md` §1).

- **Command:**
  ```sh
  gh api repos/MosslandOpenDevs/links/private-vulnerability-reporting
  gh label list --repo MosslandOpenDevs/links
  ```
- **Captured:** 2026-07-18.
- **Observed:**
  - Private Vulnerability Reporting → `{"enabled":true}`; repository `visibility: public`, `has_issues: true`.
  - The contact link in `.github/ISSUE_TEMPLATE/config.yml` points at `https://github.com/MosslandOpenDevs/links/security/advisories/new`, which the enabled setting makes reachable — so `SECURITY.md`'s "do not open a public issue" routing now terminates somewhere real.
  - All six labels referenced by the adopter issue forms exist: `bug`, `enhancement`, `assurance/gap`, `assurance/evidence`, `assurance/residual`, `needs-human-approval`. GitHub silently drops references to labels that do not exist, so their presence is what keeps a residual-review issue carrying its `needs-human-approval` flag.
- **Supports:** the PROFILE.md §6.3 private-reporting obligation; the disclosure routing asserted in `SECURITY.md` and `AGENTIC_ASSURANCE.md` §9.
- **Note:** this records that the channel exists and is reachable, not that any report has been handled through it.

---

## EV-RUBRIC-001 — moving the rubric into data changed no rendered output

The rubric refactor (`RES-CURATION-002`) rewired `build/generate.mjs` to derive the chip assignment and the on-page legend from `ecosystem-registry.json` `rubric` instead of from hard-coded logic and hard-coded legend rows. A refactor of the thing that decides every trust chip on an anti-phishing page needs to be demonstrably behaviour-preserving, not assumed to be.

- **Bound to:** the rubric-versioning change (registry `rubricVersion` 1.0.0).
- **Captured:** 2026-07-18.
- **Method:** snapshot the four generated files before the refactor, apply the refactor, regenerate, compare byte-for-byte.
  ```sh
  # before
  cp index.html embed.html llms.txt sitemap.xml <snapshot>/
  # after the refactor
  node build/generate.mjs
  for f in index.html embed.html llms.txt sitemap.xml; do cmp -s "$f" "<snapshot>/$f"; done
  ```
- **Observed:** all four files byte-identical (`cmp` silent for each); `git diff` reported no change to any generated file. Pre-refactor SHA-256 of `index.html` was `cb171d324066c19fd17460ff798dea8a71856afa4ef729aba6107aa3acba1aec`, unchanged after.
- **Result:** every one of the 28 rendered services received the same chip, with the same CSS class and the same `aria-label`, and the legend rendered identically — so the declared rubric reproduces the previous implementation exactly. This is why `RUBRIC.md` records `1.0.0` as a faithful reconstruction rather than a semantic change.
- **Supports:** `RES-CURATION-002` resolution; `INV-PHISH-001` (chip derivation unchanged); `INV-REG-001`.

### Negative tests of the rubric consistency checks

Captured 2026-07-18 against `.github/scripts/validate-registry.py`. Each mutation was applied to a copy, checked, and reverted:

| Mutation | Result |
|---|---|
| Delete a `stampClass` that a service uses (`governance`) | `ERROR: $.services[id='agora']: stampClass 'governance' is not declared in rubric.stampClasses` — exit 1 |
| Remove the catch-all `default` precedence rule | `ERROR: ... the last rule must be the catch-all` + orphan-definition error — exit 1 |
| Drop a chip from `legendOrder` | `ERROR: ... '베타' is defined but is missing from legendOrder, so it would render on the page without an explanation` — exit 1 |

The unmodified registry exits 0. These confirm the checks fail on real drift rather than merely existing.

---

## EV-STATUS-001 — alpha and ao verified against their live health endpoints

- **Command:**
  ```sh
  curl -s "https://alpha.moss.land/api/health?strict=1"
  curl -s "https://ao.moss.land/api/status"
  curl -s "https://alpha.moss.land/sitemap.xml" | head
  ```
- **Captured:** 2026-08-23T01:01:52Z (the `ts` / `timestamp` the services themselves returned; recorded per entry in `statusVerifiedAt`).
- **Observed:**
  - `alpha` → `{"status":"ok","service":"alpha","db":"ok","seo_pages":1642,"ts":"2026-08-23T01:01:52.092Z","worst_status":"ok"}`; `sitemap.xml` lists same-day entries (`lastmod` 2026-08-22/23), and `GET /` returns 200.
  - `ao` → `{"status":"operational",...}` with `api`, `database` and `llm_router` all `healthy`, `signal_feed` healthy with 12005 records emitted; sampled data endpoints `/api/signals`, `/api/ideas`, `/api/agents` each return HTTP 200.
- **Registry before this capture:** `alpha: "paused"`, `ao: "degraded"` — both first recorded 2026-07-06 and unchanged for 48 days, including across the 2026-08-21 registry edit (`9c7b186`).
- **Result:** both values were wrong and are corrected to `operational`, with the observation time recorded in `statusVerifiedAt` and the `note` fields re-grounded on this capture.
- **Supports:** the `RES-STATUS-DRIFT-001` re-review (this is the evidence that its "re-verified when the registry is updated" mitigation was not operating); the 2026-08-23 rows in `assurance/SYSTEM.md` §9.
- **Does not close:** `RES-STATUS-DRIFT-001` — this is a point-in-time capture, and nothing continuous replaces it. Per `assurance/SYSTEM.md` §2 that is deliberate.

---

## EV-LIFECYCLE-001 — the MIP-1 lifecycle constraints reject what they are meant to reject

Follows the precedent set for the registry gate (`assurance/SYSTEM.md` §8): a control is not evidence until it has been seen to fail on the thing it is supposed to catch.

- **Command:**
  ```sh
  python .github/scripts/test-lifecycle-rules.py
  ```
- **Method:** each case mutates a copy of `ecosystem-registry.json` in a temporary tree and runs the real `.github/scripts/validate-registry.py` against it. Both directions are tested — the violation must be rejected *and* the compliant form must be accepted, so a rule that rejected everything would fail here too.
- **Captured:** 2026-08-23, Python 3.9.6 with `jsonschema[format-nongpl]`.
- **Continuous, not a snapshot.** Unlike the 2026-07-18 registry-gate negative test, which was performed once by hand and recorded here, this one is a committed script wired into `.github/workflows/registry.yml` and re-runs on every push and pull request. Loosening a lifecycle rule turns the build red rather than going unnoticed.

| Case | MIP-1 | Expected | Result |
|---|---|---|---|
| `core` with `maintainer` only | Art. 2 | REJECT | REJECT — schema `'secondMaintainer' is a required property` + validator `lifecycle 'core' requires 'secondMaintainer'` |
| `core` with both handles | Art. 2 | ACCEPT | ACCEPT |
| `beta`, no `secondMaintainer`, no reason | Art. 3 | REJECT | REJECT — `lifecycle 'beta' is above 'lab' with no secondMaintainer, so it is an exception and requires lifecycleReason` |
| `beta`, no `secondMaintainer`, reason recorded | Art. 3 (exception) | ACCEPT | ACCEPT |
| `archive` with no reason | Art. 4 | REJECT | REJECT — `lifecycle 'archive' requires 'lifecycleReason'` |
| `lab` with no maintainer | state table | ACCEPT | ACCEPT |
| `maintainer` set to an email address | `AGENTIC_ASSURANCE.md` §9 | REJECT | REJECT — schema pattern + validator `looks like a name or an email address` |
| Unmodified registry (out-of-scope entries present) | Art. 1 scope | ACCEPT | ACCEPT |

**8/8 behaved as specified.** Every rejection was caught twice — once by the published schema, once by the validator with a message naming the article violated.

### The `required: ["lifecycle"]` guard is load-bearing

JSON Schema's `if` is satisfied *vacuously* when the named property is absent, so `{"properties": {"lifecycle": {"const": "core"}}}` alone matches every entry that has no lifecycle. The pre-existing `passportEligible` rules get away without a guard because `tier` is a required property; `lifecycle` is optional by design (MIP-1 Art. 1 scopes the obligation), so the guard is what keeps the policy off out-of-scope entries.

Removing `required: ["lifecycle"]` from all four lifecycle rules and validating the **unchanged** registry:

```text
150 schema errors across 30 entries
entries dragged in: agora, algora, alpha, ao, bithumb, bridge, city, coingecko,
coinmarketcap, coinone, disclosure, github-mossland, github-opendevs, gopax, links,
llms-txt, media, medium, monitor, moss, npc, passport, recipe, registry-json, signal,
signalmap, sitemap, upbit, x, wa
```

Upbit, Bithumb and `sitemap.xml` would each be required to name a maintainer. With the guard in place the same registry produces **0 errors**.

- **Supports:** `INV-LIFECYCLE-001`, `INV-LIFECYCLE-002`.
- **Does not close:** `RES-LIFECYCLE-001` — this proves the control works, not that any service is classified. No entry carries a lifecycle yet.
