# Threat model — links.moss.land

> **Status:** Draft, produced during Agentic Assurance Profile adoption; pending human review (PROFILE.md §4.3).
>
> **Disclosure rule:** This file is public. It states threats and impacts at a level safe for public disclosure and keeps actionable exploit detail out. Suspected exploitable findings go to GitHub Private Vulnerability Reporting (see `SECURITY.md`), never a public Issue.

---

## 1. Scope and assets

Covers the `links.moss.land` static site, its generator (`build/generate.mjs`), the source-of-truth `ecosystem-registry.json` + schema, and the AWS Amplify delivery / response-header configuration (`customHttp.yml`, `amplify.yml`).

Assets worth protecting:

- **Integrity of the authenticity signal** — the promise that a listed, non-제3자 link is genuinely Mossland's. This is the primary asset; its compromise is a phishing vector against the whole ecosystem.
- **Integrity of the registry** consumed cross-origin by Passport / City / WA (drives ecosystem stamps).
- **Availability** of the directory and the registry endpoint.
- **Reputation** — a false or hijacked entry would undermine trust in every Mossland property.

No secrets, credentials, funds, or personal data are held by this repository or site (static, no backend, no auth).

## 2. Actors and trust levels

| Actor | Trust level | Notes |
|---|---|---|
| Anonymous visitor | Untrusted | Reads the page; the audience the anti-phishing promise serves. |
| Cross-origin consumer (Passport, City, WA) | Trusting relying party | Fetches the registry and trusts its authenticity judgement. |
| Registry curator / maintainer | Privileged | Edits the registry via reviewed pull request; the main integrity boundary. |
| Mossland DAO via Agora | Governing authority | Binding decision of record for what the ecosystem officially includes (`ecosystem-registry.json` agora entry). |
| AWS Amplify | Infrastructure provider | Hosts, deploys, and applies response headers. |
| Third-party market/exchange sites | Untrusted external | Linked, explicitly labelled 제3자, never verified by Mossland. |
| Impersonator / phisher | Adversary | Wants a malicious domain to appear official, or the page framed/spoofed. |

## 3. Trust boundaries

| Boundary | Inside | Outside | Crossing mechanism |
|---|---|---|---|
| Curation | Reviewed registry state | Proposed edits, typos, compromised commits | Pull-request review + generator run |
| Delivery | Generated static artifacts | Public internet | AWS Amplify + `customHttp.yml` headers |
| Cross-origin read | Registry JSON/schema | Any web client | `Access-Control-Allow-Origin: *` (read-only) |
| Framing | Mossland origins (self, wa.moss.land) | All other origins | CSP `frame-ancestors` |

## 4. Entry points and attack surface

- The public page (`index.html`) and kiosk view (`embed.html`).
- The cross-origin registry endpoints (`/ecosystem-registry.json`, `/ecosystem-registry.schema.json`).
- The registry file in source control (the highest-value target: editing it changes what the ecosystem calls "official").
- The build/deploy path (generator + Amplify configuration).
- Supply chain: the generator is dependency-free pure Node (`build/generate.mjs:1-9`), so the third-party dependency surface is effectively nil.

## 5. Abuse cases

Stated as abuse + impact, without a working recipe:

- **False verification.** An adversary gets a non-Mossland domain listed without the 제3자 chip (via a curation error or an unreviewed edit), lending a phishing domain the site's authority. Impact: high. → `INV-PHISH-001`, `DEF-PHISH-001`.
- **Projection drift.** Committed HTML is edited by hand or shipped stale so the page diverges from the registry, showing links the source of truth does not. Impact: medium–high. → `INV-REG-001`, `DEF-REG-001`.
- **Passport-eligibility abuse.** A third-party/channel entry is marked `passportEligible: true`, letting a non-Mossland domain back an ecosystem stamp. Impact: medium. → `INV-PASSPORT-001`, `DEF-PASSPORT-001`.
- **Markup/JSON-LD injection** via registry content. Bounded by `esc()` on the body and CSP `script-src 'self'`; JSON-LD is a residual sink. Impact: low. → `INV-RENDER-001`, `DEF-RENDER-001`.
- **Clickjacking / framing** by an impersonator to overlay the trusted page. Impact: low–medium. → `INV-FRAME-001`.
- **Header regression.** A platform/config change silently drops CSP/HSTS/CORS scoping. Impact: medium. → `DEF-HTTP-001`, `RES-HEADERS-001`.

## 6. Controls mapped to invariants

| Threat | Control | Invariant ID | Verification |
|---|---|---|---|
| False verification of a domain | `owner`/`tier` → chip derivation; curation review | INV-PHISH-001 | Manual review; last-verified date (gap: no automated authenticity check) |
| Page diverges from source of truth | Generator is sole writer; no hand edits | INV-REG-001 | `node build/generate.mjs` + `git diff` (gap: not in CI) |
| Non-Mossland domain backs a stamp | Schema `allOf` forces `passportEligible:false` | INV-PASSPORT-001 | JSON Schema validation (gap: not in CI) |
| Injection via registry content | `esc()` on body + CSP `script-src 'self'` | INV-RENDER-001 | Code inspection; CSP present |
| Cross-origin misuse | `ACAO:*` scoped to read-only registry only | INV-CORS-001 | Header inspection |
| Clickjacking / framing | CSP `frame-ancestors 'self' + wa.moss.land` | INV-FRAME-001 | Header inspection |
| Trading-recommendation confusion | 제3자 chip + "reference only" notice | INV-MARKET-001 | Rendered-output inspection |

## 7. Residual links

Threats not fully controlled are residuals, not omissions:

- RES-VERIFY-001 — manual, periodic authenticity verification.
- RES-CI-VALIDATION-001 — no schema/projection validation in CI.
- RES-HEADERS-001 — deployed headers not asserted automatically.
- RES-RENDER-JSONLD-001 — JSON-LD not escaped against script-element termination.
- RES-STATUS-DRIFT-001 — service statuses lag the live services.

## 8. Review triggers

Re-review when:

- a new entry point, actor, or trust boundary is introduced (e.g. a write API, a new consumer);
- the registry schema's authenticity or Passport-eligibility rules change;
- `customHttp.yml` CSP/CORS/HSTS or the Amplify delivery path changes;
- the generator gains a runtime dependency;
- a phishing/impersonation incident or near-miss occurs;
- a linked residual reaches its `review_after` date (2026-10-18).
