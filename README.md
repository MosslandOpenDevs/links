# Mossland Verified Links

[![registry CI](https://github.com/MosslandOpenDevs/links/actions/workflows/registry.yml/badge.svg)](https://github.com/MosslandOpenDevs/links/actions/workflows/registry.yml)
[![assurance](https://github.com/MosslandOpenDevs/links/actions/workflows/assurance.yml/badge.svg)](https://github.com/MosslandOpenDevs/links/actions/workflows/assurance.yml)

The official **Verified Links** registry for `https://links.moss.land`.

This repository is the verified-links registry for the Mossland ecosystem: the
canonical list of official Mossland domains, ecosystem apps, developer resources,
and third-party market references. Anything not listed here should be treated as
unofficial. It is deployed with AWS Amplify and served at `https://links.moss.land`.

The page is **KR-primary, bilingual** (Korean lead, English support) and its core
job is anti-phishing: telling a visitor which domains are genuinely Mossland's.

**Contributing?** Read [`AGENTS.md`](AGENTS.md) first, then [Adding or changing a service](#adding-or-changing-a-service).

## Contents

- [Source of truth](#source-of-truth)
- [Files](#files)
- [Sections](#sections)
- [Chips (trust signal)](#chips-trust-signal)
- [Lifecycle (MIP-1)](#lifecycle-mip-1)
- [Conventions](#conventions)
- [Adding or changing a service](#adding-or-changing-a-service)
- [Security](#security)
- [License](#license)

## Source of truth

[`ecosystem-registry.json`](ecosystem-registry.json) is the single source of
truth. Each service is keyed by a stable `id` and carries `name`, `domain`,
`url`, `tier`, `status` and `passportEligible` (required), plus optional
`section`, `stampType`/`stampClass`, `labelKo`/`label`, `chip`,
`lifecycle`/`maintainer`/`secondMaintainer`/`lifecycleReason` and more (see
[`ecosystem-registry.schema.json`](ecosystem-registry.schema.json) for the
contract). The same file also holds the classification `rubric` and its
`rubricVersion`. Other Mossland properties (moss.land, Passport, City, WA) can
fetch it cross-origin (CORS `*`) to verify "is this a real Mossland domain?" and
to drive Passport ecosystem stamps.

**`index.html`, `embed.html`, `llms.txt`, and `sitemap.xml` are generated from
the registry.** Do not edit them by hand — edit the registry (or the
template/CSS in `build/`) and rebuild:

```sh
node build/generate.mjs
```

**Preview it locally** — the generated `index.html` is fully self-contained (CSS inlined, no runtime fetches), so open it directly:

```sh
open index.html            # macOS; or serve it, e.g. python3 -m http.server 8000
```

**CI enforces this — it is not just convention.**
[`.github/workflows/registry.yml`](.github/workflows/registry.yml) runs on every
push and pull request: it validates the registry against the schema and fails
the build if the committed pages are not byte-identical to a fresh generator
run. Check locally before pushing:

```sh
node build/generate.mjs && git diff --exit-code   # projection is clean
python .github/scripts/validate-registry.py       # registry contract + rubric
```

**Prerequisites:** Node for the generator (CI uses Node 22; there is no `package.json`) and Python 3 for the validator (CI uses 3.12) with `pip install "jsonschema[format-nongpl]"`.

The generator is pure Node (no dependencies) and idempotent. Amplify re-runs it
on deploy, but with `|| true` — so what actually ships is the committed output,
and the CI check at merge time is what guarantees it matches the registry.

## Files

| File | Role |
| --- | --- |
| `ecosystem-registry.json` | **Source of truth** — every service and its fields, plus the classification `rubric` / `rubricVersion` that drives the chips and legend |
| `ecosystem-registry.schema.json` | JSON Schema (draft 2020-12) contract for the registry |
| `assurance/RUBRIC.md` | Rubric changelog, precedence table, and version-bump rules (the rubric *itself* is data in the registry) |
| `build/generate.mjs` | Generator — renders `index.html` + `embed.html` + `llms.txt` + `sitemap.xml` from the registry, deriving chips and legend from the registry's `rubric` |
| `build/style.css` | Stylesheet, inlined into the generated HTML |
| `index.html` | Generated public page (do not edit by hand) |
| `embed.html` | Generated chrome-less kiosk view for embedding in play.wa / Mossverse |
| `llms.txt` | Generated AI-readable summary (llmstxt.org format, English) |
| `sitemap.xml` | Generated (lastmod from the registry's `generatedAt`) |
| `robots.txt` | Static crawl directives (points to the sitemap + machine files) |
| `favicon.svg`, `apple-touch-icon.png`, `og.png` | Icons + 1200×630 social card |
| `amplify.yml` | Amplify build (runs the generator) and artifact list |
| `customHttp.yml` | Amplify response headers (CSP, HSTS, COOP, CORS for the registry, UTF-8 charset for .txt/.xml, etc.) |
| `.github/` | CI and templates — `workflows/registry.yml` (schema + projection checks), `workflows/assurance.yml` (assurance validator), `scripts/validate-registry.py`, issue forms and the PR template |
| `AGENTS.md` | **Read first.** Agent/contributor instructions, build commands, and conventions |
| `AGENTIC_ASSURANCE.md` | How this repo adopts the OpenDevs Agentic Assurance Profile; §7 defines the material-change workflow |
| `.agentic-assurance/adoption.yaml` | The pinned upstream profile, adopted profile set, and the human owner (a named maintainers body) |
| `assurance/` | As-built system spec, invariants, claims, defeaters, residuals, threat model, and bound evidence |
| `SECURITY.md` | Vulnerability reporting — **never** a public Issue |
| `LICENSE` | MIT |

## Sections

The page renders five sections (`section` field), in order:

1. **공식 / Official** — canonical Mossland domains (Website, Disclosure) plus
   official off-domain channels (Medium, X).
2. **참여 / Participation** — things you actively use: Passport (featured), Agora,
   Mossverse.
3. **생태계 / Ecosystem** — the broader service family: intelligence (Alpha,
   Signal Map, Media), showcase (City, NPC, Recipe), and the experimental
   governance stack (MOSS.AO, Algora, BRIDGE, Governance Monitor).
4. **개발자 / Developers** — the GitHub orgs. Machine artifacts (registry JSON,
   llms.txt, sitemap) are demoted to a small footer link row, not cards.
5. **시세·거래소 / Markets** — third-party price trackers and exchanges.

## Chips (trust signal)

Color carries the meaning; each service's specifics live in its one-line role,
not the chip. There are seven chips:

| Chip | Color | Meaning | Driven by |
| --- | --- | --- | --- |
| `공식` | green on sand — the only filled chip | Verified Mossland domain or official channel | default |
| `베타` | green outline | Official service in open beta | `tier: official_beta` or `status: beta` |
| `인텔리전스` | teal outline | Mossland AI intelligence & data | `tier: intelligence` |
| `쇼케이스` | purple outline | Experiential demo & world showcase | `tier: showcase` |
| `실험` | amber outline | Experimental / not-yet-finished (not an official product) | `tier: labs`, or explicit `chip: "실험"` |
| `제3자` | grey outline | Third-party, not verified by Mossland | `owner: "third-party"` / `tier: third_party` |
| `자료` | muted | Developer data file | `artifact: true` |

> **This table is a convenience summary, not the source of truth.** The rubric is
> declared as data in [`ecosystem-registry.json`](ecosystem-registry.json) under
> `rubric`, versioned by `rubricVersion`, and `build/generate.mjs` renders both the
> chips and the on-page legend from it. Nothing checks this table against the
> rubric, so if they ever disagree, the registry wins — see
> [`assurance/RUBRIC.md`](assurance/RUBRIC.md) for the changelog, the full
> precedence table, and the version-bump rules.
>
> **Changing what a chip or `stampClass` means requires bumping `rubricVersion`**
> per `RUBRIC.md` §3, and counts as a material change under
> [`AGENTIC_ASSURANCE.md`](AGENTIC_ASSURANCE.md) §7. No check can catch a missed
> bump: Passport relies on it to know when `stampClass` meanings moved.
>
> This table has drifted before — until 2026-07-18 it claimed "five chips" and
> omitted `인텔리전스` and `쇼케이스`, which the page had been rendering all along.
> That drift is what motivated moving the rubric into data.

Key rule: **the amber `실험` stage is decoupled from operational `status`.**
`offline`/`paused` are uptime, not a stage — a service is `실험` because it *is*
experimental, set via `tier: labs` (auto) or an explicit `chip: "실험"` on a
non-labs service (e.g. `signal`, live but still data-seeding on its home view).

## Lifecycle (MIP-1)

`lifecycle` records **the maintenance promise a service carries** — separate from
`status`, which records observed availability at a point in time. An archived
service can still be reachable; a core service can be degraded. The states come
from **MIP-1** (*공개 서비스·저장소 생명주기 정책*), ratified through
[Agora](https://agora.moss.land/), which names this registry the single source of
truth for them and sets a monthly review (`lifecycleReviewedAt`).

| State | 의미 | Promise | Required fields |
|---|---|---|---|
| `core` | 상시 운영 | Maintainer + second maintainer, incident response, changes pre-announced | `maintainer`, `secondMaintainer` |
| `beta` | 운영 중, 변동 가능 | Maintainer assigned; features and data may change | `maintainer` |
| `lab` | 실험, best-effort | May change or stop without notice | — |
| `archive` | 종료·보존 | Development ended; the record is preserved read-only | `lifecycleReason` |

Two rules are enforced, not just documented — the schema's `allOf` carries them
for any consumer validating against the published contract, and CI fails the
build with a message naming the article violated:

- **No unstaffed Core.** `core` without a `secondMaintainer` is rejected.
- **No silent exception, no silent ending.** A `core`/`beta` entry without a
  `secondMaintainer` is an exception and needs `lifecycleReason`; `archive`
  always needs one. Archive is not deletion — the reason is the record of *why*.

`lifecycle` is **optional by design.** MIP-1 scopes the obligation to public
`*.moss.land` services and deployment-linked public repositories, so third-party
market entries, off-domain channels and data artifacts carry no lifecycle at all.

> **Maintainers are public handles.** `maintainer` and `secondMaintainer` take a
> GitHub handle or an `org/team` slug — never a real name or an email address.
> This is a public repository; the schema pattern and CI both reject
> address-like values.

**Status of this repository:** `links` is proposed as **Core** in MIP-1's Annex A.
The classification is not applied yet — the schema and checks landed first, and the
values follow once the mapping is approved. Tracked as `RES-LIFECYCLE-001`.

## Conventions

- **`tier`** (`official`, `official_beta`, `registry`, `companion`,
  `intelligence`, `showcase`, `world`, `runtime`, `labs`, `developer`,
  `channel`, `third_party`) is the service's nature; it drives the chip and
  Passport logic. Chip derivation is data-driven (never keyed on service id).
  Note `companion` is in the schema enum but has no entry in the registry's
  `tiers` glossary and no service uses it — dead, pending a decision to define
  or drop it.
- **Sections are presentation, separate from `tier`.** Each service renders in
  one `section`; the optional `extraSections` array can render it in more (the
  mechanism exists but is currently unused — Passport/Agora live in 참여 only).
- **`third_party` and `channel`** entries are `passportEligible: false` by
  contract. Both are pinned by the schema's `allOf`, and CI rejects a violation
  (`INV-PASSPORT-001`): exchange and price links *and* off-domain channels
  (Medium, X) never back a Passport stamp.
- **Empty-but-live services** (currently `signal`: live, but the home view still
  renders `00` counters) get an explicit `chip: "실험"` while empty; drop the chip
  once real data appears and it falls through to its **tier** chip — for `signal`
  (`tier: intelligence`) that is `인텔리전스`, not `베타`, because `인텔리전스`
  outranks `베타` in the precedence order (see
  [`assurance/RUBRIC.md`](assurance/RUBRIC.md) §4.1).
- **`lifecycle` is a governance decision, not curation.** `tier`, `chip` and
  `status` are Mossland's own editorial judgements; `lifecycle` is a Mossland DAO
  decision recorded here because MIP-1 makes this registry its source of truth.
  Changing one needs `lifecycleReason` and belongs in the monthly review, not in a
  routine registry edit.
- **Always ground descriptions in the live site.** Several labels were corrected
  by actually rendering each service (many are client-side SPAs whose homepage is
  an empty shell — check `/about` or render with JS), not by guessing.

## Adding or changing a service

> Contributors and agents: read [`AGENTS.md`](AGENTS.md) first. This repo adopts
> the OpenDevs Agentic Assurance Profile
> ([`AGENTIC_ASSURANCE.md`](AGENTIC_ASSURANCE.md)). Adding a service is routine.
> Changing what the registry **means** — a tier or chip's semantics,
> `passportEligible`, `stampClass`, a `lifecycle` state, the rubric, or the
> `customHttp.yml` headers —
> is a *material change* under §7, which means reading and updating the affected
> artifacts in [`assurance/`](assurance/) as part of the same change.

1. Edit `ecosystem-registry.json` (add/modify a service object). Base the
   `labelKo`/`label` on what the live site actually says it is. Bump `version`
   for any change to the service set, and refresh `generatedAt` when you have
   re-verified the links — it renders as the page's 최종 확인 (last-verified) date and the
   sitemap's `lastmod`.
2. If the entry needs a `stampClass` or chip the registry's `rubric` does not
   already declare, add it there too and bump `rubricVersion` per
   [`assurance/RUBRIC.md`](assurance/RUBRIC.md) §3 — CI fails on an undeclared
   `stampClass` or an orphan chip. Setting or changing a `lifecycle` also needs
   its `maintainer`/`secondMaintainer`/`lifecycleReason` companions — CI names the
   MIP-1 article if one is missing.
3. Run `node build/generate.mjs`.
4. Validate locally: `git diff --exit-code` (after regenerating),
   `python .github/scripts/validate-registry.py`, and — if you touched a
   `lifecycle` rule — `python .github/scripts/test-lifecycle-rules.py` (all need
   the validator prerequisites above).
5. Commit the registry change **and** the regenerated `index.html`,
   `embed.html`, `llms.txt`, and `sitemap.xml`. CI re-runs the generator and
   fails the build if they differ.
6. **Open a pull request** using the PR template. Registry edits are curation
   judgements about which domains are genuinely Mossland's, so they are
   reviewed — not pushed straight to `main`. That review is the human control
   behind `INV-PHISH-001`, the anti-phishing invariant.

## Security

**Never open a public Issue for a suspected vulnerability** — including a listed
domain that is not genuinely Mossland's, or a missing official domain. Both are
security issues for an anti-phishing registry.

Use GitHub's **Report a vulnerability** button under the repository's Security
tab. See [`SECURITY.md`](SECURITY.md) for scope and what a useful report
contains.

## License

MIT — see [`LICENSE`](LICENSE).
