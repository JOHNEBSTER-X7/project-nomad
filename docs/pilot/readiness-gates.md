# Controlled pilot readiness gates

This document defines go/no-go gates for a future, limited NOMAD pilot. A passing software CI run is not a pilot-readiness approval.

## Gate 0 — Discovery only
**Permitted:** meetings, non-invasive site discovery with permission, lab testing using synthetic data.

**Evidence:** verified host institution; written permission for assessment; accountable sponsor; scope and boundaries; initial risk register.

**No-go:** no named accountable institution, unclear authority, or pressure to collect learner data during discovery.

## Gate 1 — Design approval
**Required evidence:**
- Site assessment checklist completed.
- Community and educator consultation plan approved.
- Data protection/privacy and child safeguarding reviews completed by competent local advisers.
- Threat model, data flow map, retention plan and incident response plan reviewed.
- Content licensing and approval process documented.
- Network architecture and access boundaries approved by the host ICT lead.
- Qualified electrical/solar design review completed where off-grid power is proposed.
- Procurement and maintenance responsibilities agreed.

**No-go:** unresolved critical safety, privacy, safeguarding, security, copyright or electrical risks.

## Gate 2 — Lab acceptance
**Required evidence:**
- Reproducible installation from documented release.
- Functional tests for offline access, local retrieval, controlled content import and recovery.
- Security tests for operator authentication, secrets handling, network exposure and backup restoration.
- AI disabled by default; if enabled, evaluated with a reviewed test set for factuality, harmful outputs, citation accuracy, latency and local hardware limits.
- Load, thermal, storage and power measurements on the proposed hardware.
- Rollback and secure data-erasure procedure demonstrated.
- Operator training material and support contacts prepared.

**No-go:** failed critical tests, unknown data flows, unauthenticated administrative access, unsafe thermal/power behaviour or untested recovery.

## Gate 3 — Limited supervised test
**Required evidence:**
- Written final institutional authorisation and any required parent/carer and participant notices/consents, determined by local law and institutional policy.
- Test scope, duration, eligible users, supervision and stop conditions approved.
- Use synthetic or non-personal content wherever possible.
- Named incident owner and daily review process.
- No high-stakes automated learner decisions.
- Clear manual alternative if NOMAD is unavailable.

**No-go:** no meaningful supervision, unclear consent/notice requirements, or no practical stop/rollback process.

## Gate 4 — Evaluation and decision
Collect only the minimum aggregated evidence needed: availability, task completion, retrieval relevance, latency, power use, support burden, educator feedback and incidents. Avoid individual learner tracking.

The institution and project team jointly decide whether to stop, remediate, repeat or consider a separately approved next phase. A successful limited test does not automatically authorise wider rollout.

## Mandatory stop conditions
Immediately suspend the test and follow the incident plan if there is suspected unauthorised disclosure, unsafe electrical/thermal behaviour, safeguarding concern, material security compromise, unapproved external data transfer, harmful system behaviour that cannot be contained, or withdrawal of institutional permission.
