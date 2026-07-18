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
