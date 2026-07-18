# Agent instructions — Mossland Verified Links

> The "OpenDevs Agentic Assurance" section below is copied verbatim from [`AGENTIC_ASSURANCE.md`](AGENTIC_ASSURANCE.md) §11, which remains the normative source. If the two copies ever differ, `AGENTIC_ASSURANCE.md` governs.

---

## OpenDevs Agentic Assurance

This repository adopts the OpenDevs Agentic Assurance Profile pinned in
`.agentic-assurance/adoption.yaml`.

Before any material change, read:

1. `AGENTIC_ASSURANCE.md`;
2. `.agentic-assurance/adoption.yaml`;
3. the project system specification and non-goals (`assurance/SYSTEM.md`);
4. affected claims, invariants, defeaters, and residuals (`assurance/*.yaml`);
5. the active change specification (the pull request / issue).

Human-approved project intent governs project purpose. The pinned upstream
profile governs generic assurance obligations. Current implementation behavior
is not automatically intended behavior.

Do not silently weaken tests, controls, invariants, evidence obligations, or the
upstream pin. Report conflicts and unresolved uncertainty explicitly.

---

## Project overview

Mossland Verified Links (`https://links.moss.land`) is the KR-primary, bilingual, anti-phishing registry of official Mossland domains, ecosystem apps, developer resources, and third-party market references. Its core job is to tell a visitor which domains are genuinely Mossland's — anything not listed should be treated as unofficial. `ecosystem-registry.json` is the single source of truth; `index.html`, `embed.html`, `llms.txt`, and `sitemap.xml` are generated projections of it. It is a static site deployed on AWS Amplify.

Non-goals and the as-built system description live in `assurance/SYSTEM.md`.

## Build and test commands

```sh
node build/generate.mjs   # regenerate index.html + embed.html + llms.txt + sitemap.xml from the registry
git diff --exit-code      # generator is idempotent: committed output must equal a fresh run
```

- There is no unit-test suite today. The primary reproducible check is the idempotent regenerate-and-diff above.
- Do not hand-edit generated files (`index.html`, `embed.html`, `llms.txt`, `sitemap.xml`) — edit `ecosystem-registry.json` (or `build/generate.mjs` / `build/style.css`) and regenerate.
- Do not weaken, remove, or skip a check solely to obtain a green result.

## Conventions

- **Source of truth:** `ecosystem-registry.json`, validated by `ecosystem-registry.schema.json` (JSON Schema draft 2020-12). Base `labelKo`/`label` on what the live service actually says it is.
- **Change workflow:** GitHub pull requests, per `README.md` ("Source of truth", "Adding or changing a service") — matches `specification_workflow` in `.agentic-assurance/adoption.yaml`. Commit the registry change **and** the regenerated output together.
- **Trust signal:** chip derivation is data-driven off `owner`/`tier`/`chip` (never keyed on service id) — see `build/generate.mjs` `chipFor()` and `INV-PHISH-001`, `INV-MARKET-001`.
- **Passport eligibility:** `third_party` and `channel` entries are `passportEligible: false` by contract (`INV-PASSPORT-001`).
- **Security headers:** live in `customHttp.yml`; changes there are security-sensitive (`INV-CORS-001`, `INV-FRAME-001`, `DEF-HTTP-001`).
- **Security reporting:** never open a public Issue for a suspected vulnerability — see `SECURITY.md`.

Nested `AGENTS.md` files may impose stricter local rules but must not weaken the assurance adoption above.
