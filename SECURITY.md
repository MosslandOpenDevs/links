# Security Policy

## Scope

This policy covers `links.moss.land` (Mossland Verified Links) and this repository:

- the authenticity/anti-phishing signal — a listed, non-제3자 link being presented as a genuine Mossland domain when it is not, or a real Mossland domain being omitted;
- `ecosystem-registry.json` and `ecosystem-registry.schema.json` (the cross-origin source of truth consumed by other Mossland properties);
- the generator `build/generate.mjs` and the generated artifacts;
- the AWS Amplify delivery and response-header configuration (`customHttp.yml`, `amplify.yml`) — CSP, HSTS, CORS scoping, `frame-ancestors`.

A weakness in another Mossland property should be reported to that property's maintainers, unless it is caused by this registry or its shared consumption contract.

## Reporting a vulnerability

**Do not open a public GitHub Issue for a suspected vulnerability.**

Use GitHub's **Report a vulnerability** function under this repository's **Security** tab (Private Vulnerability Reporting). Maintainers should enable Private Vulnerability Reporting for `MosslandOpenDevs/links` before relying on this channel.

If private reporting is unavailable, open a public Issue that contains **no technical detail** and asks maintainers to open a private channel. Do not include a working domain-spoofing method, exploit code, or any actionable attack path in a public Issue.

A useful private report includes:

- the affected file, endpoint, deployed URL, commit, or registry entry;
- impact and a plausible abuse scenario (for example, a phishing domain gaining the site's authority);
- reproduction steps or a proof of concept;
- affected and unaffected configurations, when known;
- a suggested mitigation, when available;
- your disclosure and credit preferences.

## Handling process

Maintainers should: acknowledge and triage privately; open or accept a draft GitHub Security Advisory; reproduce and bound the issue; prepare and verify a fix (in a private working area when the detail is sensitive); determine affected deployments; ship the fix; and publish a sanitized advisory and, where relevant, an updated residual after coordinated disclosure.

An unresolved vulnerability must not be converted into a public conformance Issue merely to fit the assurance workflow.

## Public assurance versus private security detail

Public assurance artifacts under `assurance/` may state a sanitized version of an affected requirement, that evidence was refreshed, a published advisory identifier, and a non-actionable residual summary. Before authorized disclosure they must not include proof-of-concept detail, exact bypass conditions, secrets or personal data, or production topology that materially lowers attack cost. See `PROFILE.md` §13 of the pinned upstream profile (`MosslandOpenDevs/agentic-assurance-profile`).

## Disclosure principle

This registry exists to make the authenticity boundary and its residual uncertainty explicit, not to publish attack instructions. When transparency and immediate safety conflict, preserve the detail privately and publish a sanitized summary until coordinated disclosure is complete.
