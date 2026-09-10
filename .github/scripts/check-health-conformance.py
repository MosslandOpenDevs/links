#!/usr/bin/env python3
"""Probe every registered /api/health and check it against HEALTH_CONTRACT.md.

Why this exists, and why here rather than in each service's own repo:

Conformance is not a property of any service's source. For most of the
ecosystem the `Access-Control-Allow-Origin` header comes from nginx or Caddy on
a hand-managed box, not from the app — measured 2026-09-10, `passport`'s origin
at 127.0.0.1:3000 sends no ACAO at all, and `agora`'s arrives only because an
API Gateway CorsConfiguration was deleted from the AWS console. None of that is
in any repository, no service's own test suite can reach it, and every deploy
gate probes an origin *behind* the component that adds the header. So each
repo's CI is structurally blind to the failure this checks for.

The failure is also silent by construction. A consumer that cannot read a
health endpoint does not see red: monitor.moss.land's map falls back to city's
aggregate, and the service keeps a green dot sourced from a probe of an
unrelated data URL. Nothing anywhere turns a colour. That is exactly how
`signalmap` sat green for weeks while its `/api/health` was unreadable.

This runs from the registry rather than a list of ids, so a service added to
`ecosystem-registry.json` with a `statusUrl` is covered the day it lands.

What makes the build red:

  * a service that is expected to conform stops conforming — the regression
    this exists to catch;
  * a recorded exception starts conforming, so EXCEPTIONS cannot quietly rot
    into a list of things nobody rechecks;
  * every probe fails, which means the check itself is broken rather than the
    ecosystem being entirely down.

What does not: a single service being unreachable. This checks the contract,
not uptime — a timeout is reported and skipped, because failing the gate for
an outage teaches everyone to ignore it.

Usage:  python3 .github/scripts/check-health-conformance.py [--registry PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_STATUS = {"ok", "degraded", "down"}
TIMEOUT_S = 20

# A browser sends one; the header must not depend on it, so we probe with a
# foreign origin. A service that reflects only allow-listed origins passes a
# same-origin curl and still fails every real consumer.
PROBE_ORIGIN = "https://monitor.moss.land"

# Services known not to satisfy some rule, with the reason and who can fix it.
# A service listed here is still probed: if it starts conforming, the build goes
# red so the entry gets removed rather than outliving its reason.
#
# Keys are registry ids; values are the rule numbers from HEALTH_CONTRACT.md
# that entry is exempt from, and why.
# Rule 6 was open across most of the ecosystem when this check was written —
# seven of the sixteen sent no `Cache-Control` at all, because the 2026-09-09
# nginx session that added `Access-Control-Allow-Origin` and `Vary` to eight
# vhosts did not add this one. Closed 2026-09-10 by adding
# `add_header Cache-Control "no-cache" always;` to the six vhosts on the box
# reachable as `ssh mossland` (alpha needed a `location = /api/health` block
# created for it — its ACAO comes from the app, so that stays untouched there).
# `city` is the one that remains, and it is cached deliberately by its own app.
EXCEPTIONS: dict[str, dict] = {
    "npc": {
        "rules": {1, 3},
        "why": "no `service`, no `timestamp`. Manual-deploy service, no local checkout.",
    },
    "recipe": {
        "rules": {1},
        "why": "no `service`. Manual-deploy service, no local checkout.",
    },
    "city": {
        "rules": {1, 2, 3, 6},
        "why": "its /api/health is the cross-service aggregate (checkedAt/summary/services), "
               "not a report about itself, and its own Next app serves it `public, s-maxage=60, "
               "stale-while-revalidate=120` — the one entry here cached on purpose, and an app "
               "change rather than an nginx one. Manual-deploy service, no local checkout.",
    },
    "algora": {
        "rules": {1, 2},
        "why": 'answers status "running", outside the enum, and sends no `service`. '
               "lifecycle: archive — owner decision 2026-08-23, the code is frozen. "
               "Deliberately left visible rather than mapped to ok.",
    },
}

# Rule 4's documented exception: these answer 503 when unhealthy because a probe
# watches the status code and alarms on it. A non-200 from them is not a
# contract violation, and the body still has to be readable.
STATUS_CODE_SIGNALLERS = {"signal", "signalmap"}


class Probe:
    """One service's answer, and what the contract makes of it."""

    def __init__(self, sid: str, url: str):
        self.id = sid
        self.url = url
        self.reachable = False
        self.error: str | None = None
        self.code = 0
        self.headers: dict[str, str] = {}
        self.body: dict | None = None

    def fetch(self) -> None:
        req = urllib.request.Request(self.url, headers={"Origin": PROBE_ORIGIN})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as res:
                self._absorb(res.status, res.headers, res.read())
        except urllib.error.HTTPError as e:
            # A 4xx/5xx is an answer, not a failure to reach — rule 4 puts the
            # verdict in the body, so read it.
            self._absorb(e.code, e.headers, e.read())
        except Exception as e:                                  # noqa: BLE001
            self.error = f"{type(e).__name__}: {e}"

    def _absorb(self, code, headers, raw) -> None:
        self.reachable = True
        self.code = code
        self.headers = {k.lower(): v for k, v in headers.items()}
        try:
            self.body = json.loads(raw)
        except Exception:                                       # noqa: BLE001
            self.body = None

    def violations(self) -> list[tuple[int, str]]:
        """(rule number, what is wrong). Empty means conformant."""
        out: list[tuple[int, str]] = []
        b = self.body

        if b is None:
            out.append((4, f"HTTP {self.code} with no JSON body to read a verdict from"))
            return out

        if b.get("service") != self.id:
            out.append((1, f"`service` is {b.get('service')!r}, expected the registry id {self.id!r}"))

        status = b.get("status")
        if status not in CONTRACT_STATUS:
            out.append((2, f"`status` is {status!r}, not one of ok/degraded/down"))

        # Presence only. Rule 3 sanctions a build stamp for a static artifact —
        # "the document *is* the content, so its generation time is the only
        # 'now' it has" — which is why `links` and `monitor` return a timestamp
        # that does not move between calls and are conformant anyway. Asserting
        # that it advances would fail exactly the two the rule carves out.
        if not isinstance(b.get("timestamp"), str):
            out.append((3, "no `timestamp`"))

        if self.code != 200 and self.id not in STATUS_CODE_SIGNALLERS:
            out.append((4, f"HTTP {self.code}; the contract asks for an unconditional 200"))

        if self.headers.get("access-control-allow-origin") != "*":
            got = self.headers.get("access-control-allow-origin")
            out.append((5, f"Access-Control-Allow-Origin is {got!r}, expected '*'"
                           " — a browser consumer cannot read this at all"))

        cache = (self.headers.get("cache-control") or "").lower()
        if "no-store" not in cache and "no-cache" not in cache:
            out.append((6, f"Cache-Control is {self.headers.get('cache-control')!r}; "
                           "a cached health response reports the past"))

        return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", default=str(ROOT / "ecosystem-registry.json"))
    args = ap.parse_args()

    services = json.loads(Path(args.registry).read_text())["services"]
    targets = [(s["id"], s["statusUrl"]) for s in services if s.get("statusUrl")]
    if not targets:
        print("::error::registry lists no statusUrl — the check found nothing to probe")
        return 1

    failures: list[str] = []
    unreachable: list[str] = []
    conformant: list[str] = []
    excepted: list[str] = []

    print(f"Probing {len(targets)} health endpoints with Origin: {PROBE_ORIGIN}\n")

    for sid, url in targets:
        p = Probe(sid, url)
        p.fetch()

        if not p.reachable:
            unreachable.append(sid)
            print(f"  ?  {sid:<11} unreachable — {p.error}")
            continue

        broken = p.violations()
        exempt = EXCEPTIONS.get(sid, {}).get("rules", set())
        unexpected = [(n, msg) for n, msg in broken if n not in exempt]
        fixed = exempt - {n for n, _ in broken}

        if unexpected:
            failures.append(sid)
            print(f"  ✗  {sid:<11} HTTP {p.code}")
            for n, msg in unexpected:
                print(f"       rule {n}: {msg}")
        elif sid in EXCEPTIONS:
            excepted.append(sid)
            print(f"  –  {sid:<11} known exception (rules {sorted(exempt)}) — {EXCEPTIONS[sid]['why']}")
        else:
            conformant.append(sid)
            print(f"  ✓  {sid:<11} HTTP {p.code}")

        if fixed:
            failures.append(sid)
            print(f"::error::{sid} now satisfies rule(s) {sorted(fixed)} — remove them from "
                  f"EXCEPTIONS in this script so the entry cannot outlive its reason")

    # Everything failing to answer means this check is broken, not that the
    # whole ecosystem is down. Silence would read as "nothing to report".
    if len(unreachable) == len(targets):
        print("\n::error::every probe failed — the check itself is broken, not the ecosystem")
        return 1

    print(f"\n{len(conformant)} conformant · {len(excepted)} known exceptions · "
          f"{len(unreachable)} unreachable (not graded) · {len(failures)} failing")

    if unreachable:
        print("::notice::not graded because they did not answer: " + ", ".join(unreachable))

    if failures:
        print("\n::error::health contract regression: " + ", ".join(sorted(set(failures))))
        print("See HEALTH_CONTRACT.md. Note the header is usually set at the edge "
              "(nginx/Caddy/API Gateway), not in the app — check there first.")
        return 1

    print("\nAll registered health endpoints hold the contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
