# Mossland Service Health Contract

**v1 — 2026-09-09**

Every Mossland service answers the same question at the same address, in the same
three fields. Everything beyond those three is the service's own business.

This document lives next to `ecosystem-registry.json` because the contract and the
registry are two halves of one thing: the registry says which services exist, and
`statusUrl` points at the endpoint this contract describes.

## The endpoint

```
GET /api/health  ->  200 application/json
```

```json
{
  "status": "ok",
  "service": "monitor",
  "timestamp": "2026-09-09T11:14:29.846Z"
}
```

Three required keys. A service keeps every field it already publishes, unchanged
and in place — this contract only ever adds.

| key | type | meaning |
| --- | --- | --- |
| `status` | `"ok"` \| `"degraded"` \| `"down"` | can the service do its job right now |
| `service` | string | the service's `id` in `ecosystem-registry.json`, exactly |
| `timestamp` | RFC 3339, UTC | when *this response* was produced |

## Rules

### 1. `service` is the registry id, not the display name

`"npc"`, not `"Mossland NPC"`. The point of the field is that a consumer can join a
health response to its registry entry without a lookup table in between. A service
that wants to publish its human name keeps doing so under `app` or `name`.

### 2. `status` describes serving, not lifecycle

An archived service that still answers correctly reports `"ok"`. Whether it is
frozen is the registry's `lifecycle` field to say, and saying it twice — in two
vocabularies that can disagree — is how a dashboard ends up lying.

- `ok` — serving correctly.
- `degraded` — serving, but a dependency or a freshness expectation is not met.
- `down` — cannot serve its purpose.

Three values, because a badge with more than three states is a badge nobody reads.

### 3. `timestamp` is response time, never data freshness

It answers "when did this process speak", not "how fresh is the data". Those are
different failures and a service that conflates them cannot report either. Data
freshness has its own optional field, `lastProcessedAt`, and a service with no
pipeline says `"pipeline": "none"` rather than inventing one.

For a static artifact — a generated site, a built viewer — the document *is* the
content, so its generation time is the only "now" it has. Emit `timestamp` equal to
the build time and keep `pipeline: "none"` so nobody reads liveness into it.

### 4. The body is authoritative; the HTTP status is not

`200` means "this service answered". It does not mean "healthy" — `status` means
that. Keeping the two separate is what lets a consumer tell *unreachable* from
*reachable and unwell*, which are different problems with different fixes.

Two services (`signal`, `signalmap`) deliberately answer `503` when unhealthy,
because a probe watches the status code and alarms on it. That predates this
contract and still works; it is a documented exception, not a violation. The way to
have both is `alpha`'s: answer `200` at `/api/health`, and mirror `status` into the
status code at `?strict=1` for probes that can only read a number. Any service
moving from `503` to `200` **must repoint its probes in the same change** — the
failure mode otherwise is silent, and a disarmed alarm looks exactly like a healthy
service.

### 5. `Access-Control-Allow-Origin: *`

Health is public, uncredentialed liveness data — there is nothing here to protect,
and without this header a browser-side consumer cannot read it at all. This is not
a detail: it is the single reason the ecosystem view currently depends on one
aggregator instead of reading each service directly.

### 6. No cache, no auth

`Cache-Control: no-store` (or `no-cache`). A cached health response reports the
past, which is the one thing a health check must never do.

### 7. Report what you can prove

A hardcoded `{"status":"ok"}` proves only that a process is running. Where a
service has a real dependency it can cheaply check — a database ping, a corpus
that must load — check it and let `status` reflect it. Where it has none, say so
plainly rather than dressing up a constant. Not knowing is `null`, not `0` and not
`now`.

### 8. Existing paths keep working

`/healthz`, `/health`, `/api/status` stay where they are wherever they already
exist. Adding `/api/health` never removes an alias, because something unowned is
always watching the old one.

## Registering it

A service that serves this endpoint gets a `statusUrl` in `ecosystem-registry.json`:

```json
"statusUrl": "https://npc.moss.land/api/health"
```

The registry does not poll it and does not derive `status` from it — `statusUrl` is
a pointer, not a measurement. That non-goal is deliberate and is documented in
`ecosystem-registry.schema.json`.

## Checking it

`.github/scripts/check-health-conformance.py` probes every `statusUrl` in the
registry against the rules above and runs daily from `.github/workflows/
health-conformance.yml`. It sends a foreign `Origin`, because a service that
reflects only allow-listed origins passes a same-origin `curl` and still fails
every real consumer.

It lives here rather than in each service's repo because conformance is mostly
not a property of any service's source: the CORS header usually comes from
nginx, Caddy or an API gateway, and every service's own deploy gate probes an
origin *behind* that edge. Measured 2026-09-10, `passport`'s app sends no
`Access-Control-Allow-Origin` at all — it arrives from a Caddyfile on the box.

Services that do not yet satisfy a rule are listed in the script's `EXCEPTIONS`
with the reason and who can fix it. The build goes red if one of them starts
conforming, so an entry cannot outlive its reason. A service that simply does
not answer is reported and skipped: this checks the contract, not uptime, and a
gate that goes red for an outage is a gate people learn to ignore.
