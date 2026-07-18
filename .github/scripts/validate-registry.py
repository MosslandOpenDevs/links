#!/usr/bin/env python3
"""Validate ecosystem-registry.json against its published JSON Schema.

The registry is the source of truth for links.moss.land and is consumed
cross-origin by other Mossland properties, so its contract is checked on every
change rather than relying on author discipline.

Closes the schema half of RES-CI-VALIDATION-001; the projection half is the
regenerate-and-diff step in .github/workflows/registry.yml.

Checks:

1. The whole document validates against ecosystem-registry.schema.json
   (JSON Schema draft 2020-12). This is what enforces INV-PASSPORT-001 — the
   schema's allOf forbids passportEligible on third_party and channel tiers.
2. Every Passport-eligible entry is owned by Mossland. The schema encodes only
   the negative direction (third_party/channel are never eligible), so this
   explicit assertion covers the positive one that CLAIM-PASSPORT-002 states.
   Note this checks the `owner` field's value, not that the domain is genuinely
   Mossland's — that remains a curation judgement (DEF-PHISH-001).
3. Stable service ids are unique.
4. The rubric is internally consistent and covers the data: the precedence list
   ends with a catch-all, every chip a rule assigns has a definition and a legend
   row, no chip is defined that no rule can assign, and every stampClass used by a
   service is declared. The rubric is the registry's editorial contract
   (RES-CURATION-002); an inconsistency means the page could show a chip whose
   meaning is undeclared, or emit a stampClass Passport cannot interpret.

Usage: python .github/scripts/validate-registry.py
Exit code 1 on any error. No network access.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("ERROR: the 'jsonschema' package is required (pip install jsonschema)")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ecosystem-registry.json"
SCHEMA = ROOT / "ecosystem-registry.schema.json"


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        sys.exit(f"ERROR: cannot read {path.name}: {exc}")
    except json.JSONDecodeError as exc:
        sys.exit(f"ERROR: {path.name} is not valid JSON: {exc}")


def main() -> int:
    registry = load(REGISTRY)
    schema = load(SCHEMA)
    errors: list[str] = []

    # 1. Schema conformance (this is what enforces INV-PASSPORT-001).
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(registry), key=lambda e: e.json_path):
        errors.append(f"{error.json_path}: {error.message}")

    services = registry.get("services")
    if not isinstance(services, list):
        errors.append("$.services: missing or not an array")
        services = []

    # 2. Passport eligibility implies Mossland ownership (CLAIM-PASSPORT-002).
    for service in services:
        if not isinstance(service, dict):
            continue
        if service.get("passportEligible") is True and service.get("owner") != "mossland":
            errors.append(
                f"$.services[id={service.get('id')!r}]: passportEligible is true but "
                f"owner is {service.get('owner')!r}; only owner 'mossland' entries may "
                "back a Passport ecosystem stamp (CLAIM-PASSPORT-002)"
            )

    # 3. Stable identifiers are unique.
    ids = [s.get("id") for s in services if isinstance(s, dict) and s.get("id") is not None]
    for service_id, count in sorted(Counter(ids).items()):
        if count > 1:
            errors.append(f"$.services: duplicate service id {service_id!r} ({count} entries)")

    # 4. The rubric is internally consistent and covers what the data actually uses.
    # The rubric is the registry's editorial contract (RES-CURATION-002): the chip
    # rules and the stampClass meanings that build/generate.mjs renders from. An
    # inconsistency here means the page could show a chip whose meaning is undeclared,
    # or a stampClass Passport cannot interpret.
    rubric = registry.get("rubric")
    if isinstance(rubric, dict):
        chips = rubric.get("chips") if isinstance(rubric.get("chips"), dict) else {}
        precedence = chips.get("precedence") if isinstance(chips.get("precedence"), list) else []
        definitions = chips.get("definitions") if isinstance(chips.get("definitions"), dict) else {}
        legend_order = chips.get("legendOrder") if isinstance(chips.get("legendOrder"), list) else []

        rule_chips = [r.get("chip") for r in precedence if isinstance(r, dict)]

        if precedence and precedence[-1].get("when") != "default":
            errors.append(
                "$.rubric.chips.precedence: the last rule must be the catch-all "
                '{"when": "default"}, otherwise a service can match no chip at all'
            )
        for rule in precedence:
            if isinstance(rule, dict) and rule.get("chip") not in definitions:
                errors.append(
                    f"$.rubric.chips.precedence: chip {rule.get('chip')!r} is assigned by a rule "
                    "but has no entry in rubric.chips.definitions"
                )
        for name in legend_order:
            if name not in definitions:
                errors.append(
                    f"$.rubric.chips.legendOrder: {name!r} has no entry in rubric.chips.definitions"
                )
        # An orphan definition is a chip nobody can ever be assigned — usually the
        # residue of a half-finished rubric change.
        for name in definitions:
            if name not in rule_chips:
                errors.append(
                    f"$.rubric.chips.definitions: {name!r} is defined but no precedence rule assigns it"
                )
            if name not in legend_order:
                errors.append(
                    f"$.rubric.chips.definitions: {name!r} is defined but is missing from legendOrder, "
                    "so it would render on the page without an explanation"
                )

        stamp_classes = rubric.get("stampClasses") if isinstance(rubric.get("stampClasses"), dict) else {}
        for service in services:
            if not isinstance(service, dict):
                continue
            stamp_class = service.get("stampClass")
            if stamp_class is not None and stamp_class not in stamp_classes:
                errors.append(
                    f"$.services[id={service.get('id')!r}]: stampClass {stamp_class!r} is not declared "
                    "in rubric.stampClasses, so a consumer cannot tell what it signifies"
                )

    if errors:
        for message in errors:
            print(f"ERROR: {message}")
        print(f"\n{len(errors)} error(s) — registry does not satisfy its contract.")
        return 1

    eligible = sum(1 for s in services if isinstance(s, dict) and s.get("passportEligible") is True)
    rubric_version = registry.get("rubricVersion")
    chip_count = len(((registry.get("rubric") or {}).get("chips") or {}).get("definitions") or {})
    print(
        f"OK: {len(services)} services validate against ecosystem-registry.schema.json; "
        f"{eligible} Passport-eligible, all owned by Mossland; ids unique; "
        f"rubric v{rubric_version} consistent ({chip_count} chips declared)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
