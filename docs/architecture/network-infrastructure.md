# NOMAD Network Infrastructure — V0.4

## Scope

V0.4 establishes a low-risk observability foundation for a single NOMAD edge host on a local area network. It adds a status API and an operator-facing view of the API, optional local AI runtime, knowledge index, configured network mode and external synchronisation posture.

## Safety boundary

This release does not perform LAN scanning, enumerate connected devices, manage access points, administer credentials, configure firewall rules, or expose client IP addresses. Device discovery remains disabled. The status endpoint reports only coarse service state and operator-configured settings.

The dashboard is informational, not an authenticated management console. Do not expose it to an untrusted network or treat it as an administrative control plane.

## Configuration

- `NOMAD_NETWORK_MODE`: `lan` (default) or `standalone`.
- `NOMAD_EXTERNAL_SYNC_ENABLED`: `false` by default; set to `true` only after reviewing data flows and site policy.

The current endpoint reports `connectivity: local_only`; internet reachability and WAN failover are not yet measured. External sync is a configuration declaration only; no sync engine is implemented.

## API

`GET /api/network/status` returns the configured mode, local-only posture, coarse service statuses and explicit safety flags. It does not return hostnames, addresses, connected-client identities or network credentials.

## Next engineering gates

1. Define operator identity and authentication before privileged actions.
2. Threat-model device inventory and discovery; obtain explicit site authorisation before active probes.
3. Define network segmentation and guest/learner/operator trust boundaries.
4. Add a signed, auditable configuration workflow before changing network settings.
5. Validate Wi-Fi coverage, concurrent-client performance and failover on representative hardware.
6. Design content synchronisation with allowlisted sources, integrity checks, conflict handling and operator approval.

No school deployment, network equipment integration, captive portal, mesh networking or production monitoring is claimed by this prototype.
