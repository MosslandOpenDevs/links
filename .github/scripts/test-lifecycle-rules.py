#!/usr/bin/env python3
"""Negative test for the MIP-1 lifecycle constraints.

A control is not evidence until it has been seen to fail on the thing it is meant
to catch. When the registry gate was introduced this was done once by hand and
recorded in assurance/evidence/EVIDENCE.md; this script makes the same proof
re-run on every change, so the rules cannot be quietly loosened without a red
build. Recorded as EV-LIFECYCLE-001, backing INV-LIFECYCLE-001 / INV-LIFECYCLE-002.

Both directions are tested for each rule: the violation must be REJECTED and the
compliant form must be ACCEPTED, so a rule that simply rejects everything fails
here too.

The last case is the guard proof. JSON Schema's `if` is satisfied vacuously when
the named property is absent, so `{"properties": {"lifecycle": {"const": "core"}}}`
alone matches every entry that has no lifecycle. The pre-existing passportEligible
rules get away without a guard because `tier` is a required property; `lifecycle`
is optional by design (MIP-1 Art. 1 scopes the obligation to *.moss.land services),
so `required: ["lifecycle"]` is what keeps the policy off Upbit and sitemap.xml.
Removing it must break the unchanged registry.

Usage: python .github/scripts/test-lifecycle-rules.py
Exit code 1 if any case does not behave as specified. No network access.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("ERROR: the 'jsonschema' package is required (pip install jsonschema)")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ecosystem-registry.json"
SCHEMA = ROOT / "ecosystem-registry.schema.json"
VALIDATOR = ROOT / ".github" / "scripts" / "validate-registry.py"

BASE = json.loads(REGISTRY.read_text(encoding="utf-8"))
HANDLE = "MosslandOpenDevs"
TEAM = "MosslandOpenDevs/registry-maintainers"


LIFECYCLE_FIELDS = ("lifecycle", "maintainer", "secondMaintainer", "lifecycleReason")


def entry(registry: dict, service_id: str) -> dict:
    return next(s for s in registry["services"] if s.get("id") == service_id)


def reset(registry: dict, service_id: str) -> dict:
    """Strip a service's lifecycle fields before a mutation.

    The registry now ships real MIP-1 values, so a mutation like "beta with no
    reason" must first remove the reason the entry legitimately carries —
    otherwise the violation under test never exists and the case silently stops
    testing anything."""
    svc = entry(registry, service_id)
    for field in LIFECYCLE_FIELDS:
        svc.pop(field, None)
    return svc


def run_validator(registry: dict) -> tuple[int, str]:
    """Run the real validator against a mutated copy in an isolated tree."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".github" / "scripts").mkdir(parents=True)
        shutil.copy(SCHEMA, root / SCHEMA.name)
        shutil.copy(VALIDATOR, root / ".github" / "scripts" / VALIDATOR.name)
        (root / REGISTRY.name).write_text(
            json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        proc = subprocess.run(
            [sys.executable, str(root / ".github" / "scripts" / VALIDATOR.name)],
            capture_output=True,
            text=True,
        )
    return proc.returncode, proc.stdout


CASES = [
    ("core with only one maintainer", "REJECT", "MIP-1 Art. 2",
     lambda r: reset(r, "agora").update(lifecycle="core", maintainer=HANDLE)),
    ("core with both maintainers", "ACCEPT", "MIP-1 Art. 2 satisfied",
     lambda r: reset(r, "agora").update(lifecycle="core", maintainer=HANDLE, secondMaintainer=TEAM)),
    ("beta above the cap, unstaffed, no reason", "REJECT", "MIP-1 Art. 3",
     lambda r: reset(r, "wa").update(lifecycle="beta", maintainer=HANDLE)),
    ("beta above the cap, unstaffed, reason recorded", "ACCEPT", "MIP-1 Art. 3 exception",
     lambda r: reset(r, "wa").update(lifecycle="beta", maintainer=HANDLE,
                                     lifecycleReason="Second maintainer search open; published as Beta per Annex A.")),
    ("archive without grounds", "REJECT", "MIP-1 Art. 4",
     lambda r: reset(r, "media").update(lifecycle="archive")),
    ("lab needs no maintainer", "ACCEPT", "MIP-1 state table",
     lambda r: reset(r, "bridge").update(lifecycle="lab")),
    ("maintainer recorded as an email address", "REJECT", "AGENTIC_ASSURANCE.md 9 — public repo",
     lambda r: reset(r, "agora").update(lifecycle="core", maintainer="someone@example.com",
                                        secondMaintainer=HANDLE)),
    ("unmodified registry (with the applied MIP-1 values)", "ACCEPT",
     "the shipped classification satisfies every rule; out-of-scope entries untouched",
     lambda r: None),
]


def guard_is_load_bearing() -> tuple[bool, str]:
    """Removing `required: ["lifecycle"]` must break the unchanged registry."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    stripped = 0
    for rule in schema["$defs"]["service"]["allOf"]:
        guard = rule.get("if", {}).get("required") or []
        if "lifecycle" in guard:
            rule["if"].pop("required")
            stripped += 1
    if not stripped:
        return False, "no lifecycle rule carries a required:[lifecycle] guard — the guard is gone"
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(BASE))
    dragged = sorted(
        {BASE["services"][e.path[1]]["id"] for e in errors if len(e.path) > 1 and e.path[0] == "services"}
    )
    if not errors:
        return False, f"guard removed from {stripped} rules, yet the registry still validates — the guard is not doing anything"
    return True, f"guard removed from {stripped} rules -> {len(errors)} errors across {len(dragged)} entries (e.g. {', '.join(dragged[:4])})"


def main() -> int:
    failures = 0
    for name, expect, article, mutate in CASES:
        registry = copy.deepcopy(BASE)
        mutate(registry)
        code, out = run_validator(registry)
        got = "REJECT" if code else "ACCEPT"
        ok = got == expect
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  [{got:6}] {name}  ({article})")
        if not ok:
            for line in out.splitlines():
                print(f"        {line}")

    ok, detail = guard_is_load_bearing()
    failures += not ok
    print(f"{'PASS' if ok else 'FAIL'}  [GUARD ] required:[lifecycle] is load-bearing")
    print(f"        {detail}")

    if failures:
        print(f"\n{failures} case(s) did not behave as specified.")
        return 1
    print(f"\nOK: {len(CASES)} lifecycle cases plus the guard proof behaved as specified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
