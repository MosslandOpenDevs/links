# Evidence records

Reproducible evidence bound to a revision or deployment, referenced by stable IDs
from the assurance registers (PROFILE.md §11 of the pinned upstream profile).
Each record states how to reproduce it and what it supports. An AI narrative is
not evidence; the commands and their observed output are.

---

## EV-PROJECTION-b53be92 — the committed pages are a pure projection of the registry

- **Bound to:** commit `b53be92` (worktree HEAD at capture time).
- **Captured:** 2026-07-18.
- **Command:**
  ```sh
  node build/generate.mjs && git diff --quiet && echo CLEAN
  ```
- **Observed:** generator reported "Generated index.html + embed.html + llms.txt — 28 visible links across 5 sections."; `git diff --quiet` exited 0 (`CLEAN`) — the committed `index.html`, `embed.html`, `llms.txt`, and `sitemap.xml` are byte-identical to a fresh run of the generator against the committed `ecosystem-registry.json`.
- **Supports:** `INV-REG-001` (pure projection) at this revision; `CLAIM-REG-001`.
- **Does not close:** `DEF-REG-001` / `RES-CI-VALIDATION-001` — nothing in CI enforces this on every future commit; it was verified once, at this revision.

---

## EV-HEADERS-2026-07-18 — deployed responses carry the declared security headers

- **Bound to:** the live `links.moss.land` deployment as observed 2026-07-18 (one-time manual capture, not a continuous check).
- **Command:**
  ```sh
  curl -sSI https://links.moss.land/
  curl -sSI https://links.moss.land/ecosystem-registry.json
  ```
- **Observed (headers only):**
  - `GET /` → `HTTP/2 200`; `content-security-policy: default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; form-action 'none'; frame-ancestors 'self' https://wa.moss.land https://*.wa.moss.land; upgrade-insecure-requests`; `strict-transport-security: max-age=63072000; includeSubDomains`; `x-content-type-options: nosniff`; `referrer-policy: strict-origin-when-cross-origin`; `cross-origin-opener-policy: same-origin-allow-popups`; `permissions-policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()`.
  - `GET /ecosystem-registry.json` → `HTTP/2 200`; `access-control-allow-origin: *`; `cross-origin-resource-policy: cross-origin`; `cache-control: public, max-age=300`; `content-type: application/json`.
- **Result:** the served responses match `customHttp.yml` exactly, including the scoped CORS `*` on the registry and the `frame-ancestors` allow-list.
- **Supports:** `INV-CORS-001` (CORS scoped to the read-only registry), `INV-FRAME-001` (framing restricted to Mossland origins).
- **Does not close:** `RES-HEADERS-001` — this is a single manual capture, not an automated/continuous regression check.
