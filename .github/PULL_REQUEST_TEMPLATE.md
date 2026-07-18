## Summary

<!-- Intent, non-goals, and the registry/generator/config changes made. For registry-meaning changes, state what the projection and any cross-origin consumer will see. -->

## Related issue or advisory

<!-- Use `Closes #N` only when this pull request fully satisfies the issue's acceptance criteria, including evidence and durable artifact updates. Otherwise use `Related to #N`. Reference published advisories rather than reproducing confidential detail. -->

## Affected assurance IDs

<!-- List affected CLAIM-, INV-, DEF-, and RES- identifiers, or state "none". -->

- 

## Change classification

- [ ] Implementation-only — no externally visible behavior change
- [ ] Behavioral — the rendered directory or registry output changes
- [ ] Public-claim — public claims or their limitations change
- [ ] Security-sensitive — `customHttp.yml` headers, CORS, or trust boundaries
- [ ] Data-semantics — registry meaning, identifiers, tiers, or Passport eligibility

## Verification evidence

<!-- Bind evidence to a commit SHA or deployment. "All checks passed" is not evidence unless linked and reproducible. -->

- Generator idempotency: `node build/generate.mjs && git diff --exit-code`
- Registry schema validity (if changed):
- Deployed headers / live-site check (if relevant):
- Independent review:

## Residual impact

- [ ] None
- [ ] Residuals added or updated — RES- IDs listed above
- [ ] Residuals resolved — RES- IDs listed above

## Completion checklist

- [ ] Registry change and regenerated output committed together
- [ ] Enforcement present for affected invariants
- [ ] Evidence bound to a revision or deployment
- [ ] Durable assurance artifacts updated — claims, invariants, defeaters, residuals
- [ ] Public disclosure reviewed — no secrets, personal data, or actionable vulnerability detail
