# links

Mossland **Verified Links** — the official link registry for `https://links.moss.land`.

This repository is the verified-links registry for the Mossland ecosystem: the
canonical list of official Mossland domains, ecosystem apps, developer resources,
and third-party market references. Anything not listed here should be treated as
unofficial. It is deployed with AWS Amplify and served at `https://links.moss.land`.

The page is **KR-primary, bilingual** (Korean lead, English support) and its core
job is anti-phishing: telling a visitor which domains are genuinely Mossland's.

## Source of truth

[`ecosystem-registry.json`](ecosystem-registry.json) is the single source of
truth. Each service carries `tier`, `status`, `section`, `chip`,
`passportEligible`, `stampType`, `labelKo`/`label`, and more (see
[`ecosystem-registry.schema.json`](ecosystem-registry.schema.json) for the
contract). Other Mossland properties (moss.land, Passport, City, WA) can fetch
it cross-origin (CORS `*`) to verify "is this a real Mossland domain?" and to
drive Passport ecosystem stamps.

**`index.html`, `embed.html`, `llms.txt`, and `sitemap.xml` are generated from
the registry.** Do not edit them by hand — edit the registry (or the
template/CSS in `build/`) and rebuild:

```sh
node build/generate.mjs
```

The generator is pure Node (no dependencies) and idempotent; Amplify runs it on
every deploy.

## Files

| File | Role |
| --- | --- |
| `ecosystem-registry.json` | **Source of truth** — every service and its fields |
| `ecosystem-registry.schema.json` | JSON Schema (draft 2020-12) contract for the registry |
| `build/generate.mjs` | Generator — renders `index.html` + `embed.html` + `llms.txt` + `sitemap.xml` from the registry |
| `build/style.css` | Stylesheet, inlined into the generated HTML |
| `index.html` | Generated public page (do not edit by hand) |
| `embed.html` | Generated chrome-less kiosk view for embedding in play.wa / Mossverse |
| `llms.txt` | Generated AI-readable summary (llmstxt.org format, English) |
| `sitemap.xml` | Generated (lastmod from the registry's `generatedAt`) |
| `robots.txt` | Static crawl directives (points to the sitemap + machine files) |
| `favicon.svg`, `apple-touch-icon.png`, `og.png` | Icons + 1200×630 social card |
| `amplify.yml` | Amplify build (runs the generator) and artifact list |
| `customHttp.yml` | Amplify response headers (CSP, HSTS, COOP, CORS for the registry, UTF-8 charset for .txt/.xml, etc.) |

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
not the chip. There are five chips:

| Chip | Color | Meaning | Driven by |
| --- | --- | --- | --- |
| `공식` | green | Verified Mossland domain or official channel | default |
| `베타` | green outline | Official service in open beta | `tier: official_beta` or `status: beta` |
| `실험` | amber | Experimental / not-yet-finished (not an official product) | `tier: labs`, or explicit `chip: "실험"` |
| `제3자` | grey | Third-party, not verified by Mossland | `owner: "third-party"` / `tier: third_party` |
| `자료` | muted | Developer data file | `artifact: true` |

Key rule: **the amber `실험` stage is decoupled from operational `status`.**
`offline`/`paused` are uptime, not a stage — a service is `실험` because it *is*
experimental, set via `tier: labs` (auto) or an explicit `chip: "실험"` on a
non-labs service (e.g. `media`, which is live but still data-seeding).

## Conventions

- **`tier`** (`official`, `official_beta`, `registry`, `companion`,
  `intelligence`, `showcase`, `world`, `runtime`, `labs`, `developer`,
  `channel`, `third_party`) is the service's nature; it drives the chip and
  Passport logic. Chip derivation is data-driven (never keyed on service id).
- **Sections are presentation, separate from `tier`.** Each service renders in
  one `section`; the optional `extraSections` array can render it in more (the
  mechanism exists but is currently unused — Passport/Agora live in 참여 only).
- **Markets / third-party** entries are `passportEligible: false` by contract —
  exchange and price links live here, never in Passport.
- **Empty-but-live services** (e.g. Media: live but 0 data) get an explicit
  `chip: "실험"` while empty; drop the chip once real data appears and they fall
  through to `베타` (`status: beta`).
- **Always ground descriptions in the live site.** Several labels were corrected
  by actually rendering each service (many are client-side SPAs whose homepage is
  an empty shell — check `/about` or render with JS), not by guessing.

## Adding or changing a service

1. Edit `ecosystem-registry.json` (add/modify a service object). Base the
   `labelKo`/`label` on what the live site actually says it is.
2. Run `node build/generate.mjs`.
3. Commit the registry change **and** the regenerated `index.html`,
   `embed.html`, `llms.txt`, and `sitemap.xml`.
