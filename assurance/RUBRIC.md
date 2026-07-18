# Classification rubric — links.moss.land

The **rubric** is how this registry turns a service's raw fields into an editorial judgement: which trust chip a visitor sees, and what a Passport `stampClass` signifies.

> **Authoritative source:** the `rubric` object in [`ecosystem-registry.json`](../ecosystem-registry.json), versioned by `rubricVersion`.
> This file is the changelog and the rules for changing it. Where the two disagree, the registry is the rubric; this file is stale and should be fixed.

Closes `RES-CURATION-002`.

---

## 1. Why the rubric is versioned separately

`version` versions the registry *document* — the set of services and their fields. `rubricVersion` versions the *meaning* those fields carry.

They move independently, and that is the point:

- A service can be added or removed with **no rubric change** — the classification rules did not move.
- The rubric can change with **no service change** — every entry is byte-identical, yet what they *mean* is different.

The second case is the dangerous one, and it was invisible before this file existed. `stampClass` is consumed by **Passport** to weight ecosystem stamps. If the significance of `governance` or `core` were redefined and nothing in the registry changed, Passport would keep applying its old weighting to a new meaning, silently. `rubricVersion` is the signal that makes that visible.

## 2. Where it is enforced

The rubric is data, not prose, so the code cannot drift from it:

- `build/generate.mjs` derives **both** the chip assignment (`chipFor`) and the on-page legend from `rubric.chips`. A chip's rendered meaning cannot disagree with the rule that assigns it, because both read the same object.
- `.github/scripts/validate-registry.py` (run by `.github/workflows/registry.yml` on every push and pull request) checks that the rubric is internally consistent and covers the data: the precedence list ends with a catch-all, every chip a rule assigns has a definition and a legend row, no chip is defined that no rule can assign, and every `stampClass` used by a service is declared.

Not enforced: the summary table in [`README.md`](../README.md) is a human convenience copy and is **not** checked against the rubric. It can drift; the registry governs. This is an instance of the general problem tracked as `RES-PROVENANCE-001`.

## 3. Version-bump rules

The test that decides the bump is:

> **Would an unchanged service entry now render differently, or mean something different to a consumer?**

| Bump | When | Consumer obligation |
|---|---|---|
| **MAJOR** | The meaning of an existing chip or `stampClass` changes; one is removed; or precedence changes such that an unchanged entry gets a different chip. Anything that silently re-interprets existing entries. | Consumers **must** re-check their assumptions. Passport must re-examine its stamp weighting before accepting the new registry. |
| **MINOR** | Purely additive: a new chip or `stampClass` is introduced, or a new rule is added that only classifies entries no existing rule claimed. Existing entries keep their meaning. | Consumers may ignore, but should confirm they handle the new value. |
| **PATCH** | Presentation only: legend wording, translation, `aria` text, CSS class. No classification semantics change. | None. |

A rubric change is a **material change** under `AGENTIC_ASSURANCE.md` §7 — it affects public claims and a downstream consumer's behaviour — so it needs a change specification, not just a commit.

## 4. Current rubric — `1.0.0`

### 4.1 Chip precedence (first match wins)

Order matters. The `실험` override deliberately outranks the tier chips, so an empty-but-live intelligence service (e.g. `media`) shows `실험` until it has real data.

| # | Chip | Assigned when |
|---|---|---|
| 1 | `자료` | `artifact: true` |
| 2 | `실험` | explicit `chip: "실험"` **or** `tier: labs` |
| 3 | `제3자` | `owner: third-party` **or** `tier: third_party` |
| 4 | `쇼케이스` | `tier: showcase` |
| 5 | `인텔리전스` | `tier: intelligence` |
| 6 | `베타` | `tier: official_beta` **or** `status: beta` |
| 7 | `공식` | *(default — everything else)* |

### 4.2 Chip meanings

| Chip | Meaning |
|---|---|
| `공식` | Verified Mossland domains and channels |
| `베타` | Official service in open beta |
| `인텔리전스` | Mossland AI intelligence & data |
| `쇼케이스` | Experiential demo & world showcase |
| `실험` | Experimental, not a finished official product |
| `제3자` | Third-party, not verified by Mossland |
| `자료` | Developer & data files |

### 4.3 `stampClass` significance

| Class | Signifies |
|---|---|
| `core` | identity / holder |
| `governance` | binding decision acts |
| `participation` | recurring community activity |
| `connect` | lightweight verified-domain visit |
| `lab` | experimental observer |
| `showcase` | experience visit |

**Numeric weights are not defined here, deliberately.** This registry declares what a class *signifies*; how heavily to weight it is Passport's policy, in Passport's repository. Recording a weight here would assert authority over another system's behaviour that this project does not have. The registry's contribution is the meaning and the version — enough for Passport to know when to re-check.

## 5. Changelog

### `1.0.0` — 2026-07-18

Initial declaration. The rubric was **reconstructed from the existing implementation, not redesigned** — `build/generate.mjs` `chipFor()` and the hard-coded legend were the de-facto rubric, and this version writes down exactly what they already did.

Verified behaviour-preserving: after moving the rubric into data and rewiring the generator to read it, `node build/generate.mjs` produced `index.html`, `embed.html`, `llms.txt` and `sitemap.xml` **byte-identical** to the pre-refactor output. No visitor-visible change, no `stampClass` meaning change — so this is a `1.0.0` baseline rather than a semantic change to an earlier rubric.

Prior to this version the rubric existed only as code plus prose, with no version and no changelog; a change to it was invisible to consumers. That gap was `RES-CURATION-002`.
