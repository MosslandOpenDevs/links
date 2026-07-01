# links

Mossland **Verified Links** — the official link registry for `https://links.moss.land`.

This repository is the verified-links registry for the Mossland ecosystem: the
canonical list of official Mossland domains, ecosystem apps, labs, community
channels, and third-party market references. Anything not listed here should be
treated as unofficial. It is deployed with AWS Amplify and served at
`https://links.moss.land`.

## Source of truth

[`ecosystem-registry.json`](ecosystem-registry.json) is the single source of
truth. It describes every Mossland service with `tier`, `status`,
`passportEligible`, `stampType`, and more (see
[`ecosystem-registry.schema.json`](ecosystem-registry.schema.json) for the
contract). Other Mossland properties (moss.land, Passport, City, WA) can fetch
it cross-origin to verify "is this a real Mossland domain?" and to drive
Passport ecosystem stamps.

**`index.html`, `embed.html`, and `llms.txt` are generated from the registry.**
Do not edit them by hand — edit the registry (or the template/CSS) and rebuild:

```sh
node build/generate.mjs
```

## Files

| File | Role |
| --- | --- |
| `ecosystem-registry.json` | **Source of truth** — every service, tier, status, Passport eligibility |
| `ecosystem-registry.schema.json` | JSON Schema (draft 2020-12) contract for the registry |
| `build/generate.mjs` | Generator — renders `index.html` + `embed.html` + `llms.txt` from the registry |
| `build/style.css` | Stylesheet used by the generator (inlined into the HTML) |
| `index.html` | Generated public page (do not edit by hand) |
| `embed.html` | Generated chrome-less kiosk view for embedding in play.wa / Mossverse |
| `llms.txt` | Generated AI-readable summary (llmstxt.org format) |
| `robots.txt` / `sitemap.xml` | Crawlability |
| `favicon.svg`, `apple-touch-icon.png`, `og.png` | Icons + 1200×630 social card |
| `amplify.yml` | Amplify build (runs the generator) and artifact list |
| `customHttp.yml` | Amplify response headers (CSP, HSTS, CORS for the registry, etc.) |

## Conventions

- **Tiers** (`official`, `official_beta`, `registry`, `companion`,
  `intelligence`, `showcase`, `world`, `runtime`, `labs`, `developer`,
  `channel`, `third_party`) drive both the visible chip/section and consumer
  logic. **Chip text/color is derived from tier/status/artifact** (not the id
  string); the one branch that also consults `owner` is the third-party check.
  The intent it encodes: green (`공식`/`베타`) = Mossland-owned and verified,
  including official off-domain channels (X, Medium, GitHub); amber
  (`실험실`/`연구`) = genuinely experimental/research services (AO, Algora,
  BRIDGE — they self-declare it); grey (`제3자`) = genuine third-party only
  (exchanges, price trackers). Dev data files carry a muted `자료` chip.
- **Sections** are presentation, separate from `tier`. Each service renders in
  one `section`; the optional `extraSections` array can render it in more (the
  mechanism exists but is currently unused). The 생태계 (Ecosystem) section holds
  non-core services; experimental ones are marked only by their amber chip, so
  operational apps (Alpha, City…) stay 공식.
- **Markets / third-party** entries are `passportEligible: false` by contract —
  exchange and price links live here, never in Passport.
- **Media** is kept in the registry as `paused`/`hidden` until its data is
  connected (per ecosystem strategy: do not surface empty services).

## Adding or changing a link

1. Edit `ecosystem-registry.json` (add/modify a service object).
2. Run `node build/generate.mjs`.
3. Commit the registry change **and** the regenerated `index.html` /
   `embed.html` / `llms.txt`.
