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
5. The MIP-1 lifecycle policy holds (INV-LIFECYCLE-001, INV-LIFECYCLE-002). The
   rules are not hard-coded here: they are read from `rubric.lifecycle`, the same
   arrangement the chip rules use, so the declared promise and the enforced check
   are one declaration. Article 2 — a core service names a maintainer and a second
   maintainer. Article 3 — without a second maintainer a service is capped at
   `unstaffedCap`, and holding it above that cap requires a recorded reason.
   Article 4 — an archive state requires its grounds. The schema's allOf carries
   the same constraints for consumers validating against the published contract;
   this restates them so a CI failure names the article it violated.
6. Maintainer handles carry no personal data. This is a public repository
   (AGENTIC_ASSURANCE.md section 9), so a maintainer is a GitHub handle or an
   org/team slug, never a name or an email address.

Non-fatal notes (printed, exit code unaffected): services in MIP-1 Article 1 scope
that carry no lifecycle yet, and a lifecycle review older than the monthly cadence
Article 4 sets. These are reported rather than enforced because a date-triggered
hard failure would break an unrelated pull request that changed nothing.

Usage: python .github/scripts/validate-registry.py
Exit code 1 on any error. No network access.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("ERROR: the 'jsonschema' package is required (pip install jsonschema)")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ecosystem-registry.json"
SCHEMA = ROOT / "ecosystem-registry.schema.json"

# MIP-1 Art. 4 reviews the lifecycle states monthly; a few days of slack keeps the
# note from firing on a review that landed a little late.
REVIEW_CADENCE_DAYS = 35


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

    # 5. The MIP-1 lifecycle policy, enforced from its own declaration in the rubric.
    # rubric.lifecycle states what each lifecycle promises AND which fields that
    # promise requires, so the policy a reader sees and the rule CI applies are the
    # same object — the arrangement that keeps the chip rules from drifting.
    lifecycle_rubric = (rubric or {}).get("lifecycle") if isinstance(rubric, dict) else None
    notes: list[str] = []
    if isinstance(lifecycle_rubric, dict):
        states = lifecycle_rubric.get("states") if isinstance(lifecycle_rubric.get("states"), dict) else {}
        order = lifecycle_rubric.get("order") if isinstance(lifecycle_rubric.get("order"), list) else []
        cap = lifecycle_rubric.get("unstaffedCap")
        # MIP-1 articles, quoted in the failure so a red build names the policy it broke.
        article = {
            "maintainer": "MIP-1 Art. 2 / state table (a core or beta service names a maintainer)",
            "secondMaintainer": "MIP-1 Art. 2 (core requires a second maintainer with deploy and recovery rights)",
            "lifecycleReason": "MIP-1 Art. 4 (a lifecycle change, Archive in particular, is recorded with its grounds)",
        }

        for name in states:
            if name not in order:
                errors.append(
                    f"$.rubric.lifecycle: state {name!r} is defined but missing from `order`, "
                    "so its position relative to unstaffedCap is undefined"
                )
        if cap is not None and cap not in order:
            errors.append(f"$.rubric.lifecycle.unstaffedCap: {cap!r} is not one of the states in `order`")

        for service in services:
            if not isinstance(service, dict):
                continue
            sid = service.get("id")
            lifecycle = service.get("lifecycle")
            if lifecycle is None:
                continue
            if lifecycle not in states:
                errors.append(
                    f"$.services[id={sid!r}]: lifecycle {lifecycle!r} is not declared in "
                    "rubric.lifecycle.states, so its promise is undefined"
                )
                continue

            for field in states[lifecycle].get("requires") or []:
                if not service.get(field):
                    errors.append(
                        f"$.services[id={sid!r}]: lifecycle {lifecycle!r} requires {field!r} — "
                        f"{article.get(field, 'MIP-1')}"
                    )

            # Article 3: without a second maintainer the lifecycle is capped, and
            # anything above the cap is an exception that must record why.
            if (
                not service.get("secondMaintainer")
                and cap in order
                and lifecycle in order
                and order.index(lifecycle) < order.index(cap)
                and not service.get("lifecycleReason")
            ):
                errors.append(
                    f"$.services[id={sid!r}]: lifecycle {lifecycle!r} is above {cap!r} with no "
                    "secondMaintainer, so it is an exception and requires `lifecycleReason` — "
                    "MIP-1 Art. 3 (a service without a second owner is shown at Lab or below; "
                    "an exception is recorded in the registry with its reason)"
                )

        # 6. A maintainer is a public handle, never personal data (public repository).
        for service in services:
            if not isinstance(service, dict):
                continue
            for field in ("maintainer", "secondMaintainer"):
                value = service.get(field)
                if isinstance(value, str) and ("@" in value or " " in value):
                    errors.append(
                        f"$.services[id={service.get('id')!r}]: {field} {value!r} looks like a name or an "
                        "email address; this is a public repository, so record a GitHub handle or an "
                        "org/team slug instead (AGENTIC_ASSURANCE.md section 9)"
                    )

        # Non-fatal: MIP-1 Art. 1 scope not yet classified.
        in_scope = [
            s
            for s in services
            if isinstance(s, dict)
            and s.get("owner") == "mossland"
            and s.get("tier") not in ("third_party", "channel")
            and s.get("artifact") is not True
            and str(s.get("domain", "")).endswith("moss.land")
        ]
        unclassified = [s.get("id") for s in in_scope if not s.get("lifecycle")]
        if unclassified:
            notes.append(
                f"{len(unclassified)} of {len(in_scope)} services in MIP-1 Art. 1 scope carry no "
                f"lifecycle yet ({', '.join(str(i) for i in unclassified)}). The schema and this "
                "check are in place; the classification itself is an owner decision."
            )

        # Non-fatal: Art. 4 sets a monthly review cadence.
        reviewed = registry.get("lifecycleReviewedAt")
        if not reviewed:
            notes.append(
                "lifecycleReviewedAt is not set — MIP-1 Art. 4 reviews these states once a month "
                "and records when that happened."
            )
        else:
            try:
                last = datetime.fromisoformat(str(reviewed).replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - last).days
                if age > REVIEW_CADENCE_DAYS:
                    notes.append(
                        f"lifecycleReviewedAt is {age} days old, past the {REVIEW_CADENCE_DAYS}-day "
                        "monthly cadence in MIP-1 Art. 4."
                    )
            except ValueError:
                errors.append(f"$.lifecycleReviewedAt: {reviewed!r} is not a parseable date-time")

    if errors:
        for message in errors:
            print(f"ERROR: {message}")
        print(f"\n{len(errors)} error(s) — registry does not satisfy its contract.")
        return 1

    eligible = sum(1 for s in services if isinstance(s, dict) and s.get("passportEligible") is True)
    classified = sum(1 for s in services if isinstance(s, dict) and s.get("lifecycle"))
    rubric_version = registry.get("rubricVersion")
    chip_count = len(((registry.get("rubric") or {}).get("chips") or {}).get("definitions") or {})
    print(
        f"OK: {len(services)} services validate against ecosystem-registry.schema.json; "
        f"{eligible} Passport-eligible, all owned by Mossland; ids unique; "
        f"rubric v{rubric_version} consistent ({chip_count} chips declared); "
        f"{classified} services carry a MIP-1 lifecycle, all satisfying it."
    )
    for note in notes:
        print(f"NOTE: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
