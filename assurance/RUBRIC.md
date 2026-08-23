# Classification rubric — links.moss.land

The **rubric** is how this registry turns a service's raw fields into an editorial judgement: which trust chip a visitor sees, what a Passport `stampClass` signifies, and — since `1.1.0` — what maintenance promise a `lifecycle` state carries.

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
- The same validator enforces the **lifecycle** rules *from their own declaration* — it reads `rubric.lifecycle.states[*].requires` and `rubric.lifecycle.unstaffedCap` rather than hard-coding MIP-1, so the promise a reader sees and the rule CI applies are one object. `ecosystem-registry.schema.json` carries the same constraints in its `allOf` so a consumer validating against the published schema gets them too.

Not enforced: the summary table in [`README.md`](../README.md) is a human convenience copy and is **not** checked against the rubric. It can drift; the registry governs. This is an instance of the general problem tracked as `RES-PROVENANCE-001`.

## 3. Version-bump rules

The test that decides the bump is:

> **Would an unchanged service entry now render differently, or mean something different to a consumer?**

The test covers all three axes the rubric declares: chips, `stampClass`, and `lifecycle`.

| Bump | When | Consumer obligation |
|---|---|---|
| **MAJOR** | The meaning of an existing chip, `stampClass`, or `lifecycle` state changes; one is removed; or precedence changes such that an unchanged entry gets a different chip. Anything that silently re-interprets existing entries. | Consumers **must** re-check their assumptions. Passport must re-examine its stamp weighting before accepting the new registry. |
| **MINOR** | Purely additive: a new chip, `stampClass`, or classification axis is introduced, or a new rule is added that only classifies entries no existing rule claimed. Existing entries keep their meaning. | Consumers may ignore, but should confirm they handle the new value. |
| **PATCH** | Presentation only: legend wording, translation, `aria` text, CSS class. No classification semantics change. | None. |

A rubric change is a **material change** under `AGENTIC_ASSURANCE.md` §7 — it affects public claims and a downstream consumer's behaviour — so it needs a change specification, not just a commit.

## 4. Current rubric — `1.1.0`

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

### 4.4 `lifecycle` — MIP-1 states

Adopted from **MIP-1** (*공개 서비스·저장소 생명주기 정책*, Mossland DAO / Agora). `lifecycle` is the maintenance promise a service carries. It is **orthogonal to `status`**, which reports observed availability at a point in time: an archived service can still be reachable, and a core service can be degraded.

| State | 의미 | Promise | Requires |
|---|---|---|---|
| `core` | 상시 운영 | Maintainer + second maintainer (both with deploy and recovery rights), incident response, changes pre-announced | `maintainer`, `secondMaintainer` |
| `beta` | 운영 중, 변동 가능 | Maintainer assigned; features and data may change | `maintainer` |
| `lab` | 실험, best-effort | May change or stop without notice | — |
| `archive` | 종료·보존 | Development ended; the record is preserved read-only | `lifecycleReason` |

Two rules sit on top of the table:

- **Article 3 — `unstaffedCap: "lab"`.** Without a `secondMaintainer` a service is capped at `lab`. Holding it above the cap is an exception and requires `lifecycleReason`.
- **Article 4 — recorded change.** `archive` always requires `lifecycleReason`; Archive is not deletion, and the reason is what preserves why the service ended.

`lifecycle` is **optional**. MIP-1 Article 1 scopes the obligation to public `*.moss.land` services and deployment-linked public repositories, so third-party market entries, off-domain channels, and data artifacts carry no lifecycle at all. In the schema this is why every lifecycle `allOf` guards its `if` with `required: ["lifecycle"]` — without that guard an absent lifecycle satisfies the condition vacuously and every market entry would be asked for a maintainer.

## 5. Changelog

### `1.1.0` — 2026-08-23

Added the `lifecycle` axis (`rubric.lifecycle`), adopting the four states MIP-1 ratifies — `core` / `beta` / `lab` / `archive` — together with the fields each state requires and the Article 3 `unstaffedCap`.

**MINOR, not MAJOR.** The governing test is whether an unchanged entry now renders differently or means something different. It does not: `lifecycle` is a new, optional, orthogonal axis; no chip rule reads it; no `stampClass` meaning moved; every existing entry is unchanged in both value and meaning. That is the "purely additive" row of the table in §3.

The alternative considered and **not** taken was splitting `status` into a `lifecycle` + `availability` pair with `status` retained as a derived projection. It is a tidier end state — today's `status` enum genuinely mixes availability (`operational`, `degraded`, `paused`, `offline`) with lifecycle-flavoured values (`beta`, `deprecated`) — but it re-interprets a field that moss.land, Passport, City and WA already fetch, which is a MAJOR rubric change and a consumer-coordination problem. Adding an orthogonal axis gets MIP-1 what it ratifies at MINOR cost. The split stays available as a later, separately-reviewed change.

`beta` and `deprecated` therefore remain in the `status` enum, and `status: "beta"` still drives the 베타 chip (§4.1 rule 6). Where the two axes could disagree, **`lifecycle` is the authority for MIP-1 purposes** and `status` remains a point-in-time availability observation.

### `1.0.0` — 2026-07-18

Initial declaration. The rubric was **reconstructed from the existing implementation, not redesigned** — `build/generate.mjs` `chipFor()` and the hard-coded legend were the de-facto rubric, and this version writes down exactly what they already did.

Verified behaviour-preserving: after moving the rubric into data and rewiring the generator to read it, `node build/generate.mjs` produced `index.html`, `embed.html`, `llms.txt` and `sitemap.xml` **byte-identical** to the pre-refactor output. No visitor-visible change, no `stampClass` meaning change — so this is a `1.0.0` baseline rather than a semantic change to an earlier rubric.

Prior to this version the rubric existed only as code plus prose, with no version and no changelog; a change to it was invisible to consumers. That gap was `RES-CURATION-002`.
