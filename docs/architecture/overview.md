# PROJECT NOMAD — Architecture Overview

## Status

This document describes the proposed architecture for research and prototyping. It is not a record of a deployed system.

## Design goals

- Essential services operate on a local network without continuous internet access.
- Local inference and knowledge retrieval are possible on appropriately sized hardware.
- School and community data remain under local control.
- Operators can install, update, back up and recover the system using documented procedures.
- Optional external connectivity is explicit and controllable.

## Logical components

1. **User experience:** browser-based portal / PWA for teachers, learners and authorised operators.
2. **Local gateway:** API entry point, service routing and access control.
3. **AI service:** local model runtime; model choice depends on quality, hardware, safety and licence evaluation.
4. **Knowledge service:** ingestion of approved resources, indexing, retrieval and citations to source material.
5. **Persistence:** local database, document store and backup.
6. **Operations:** health checks, logs, updates, restore and power monitoring.
7. **Network and energy:** LAN/Wi-Fi and site-appropriate power resilience.

## Data flow

A user reaches the portal over the local network. The portal calls the local gateway. After authentication and authorisation, the gateway routes an approved request to the knowledge service and/or local AI runtime. Retrieval should return source references so users can inspect supporting material. No external AI call should occur unless explicitly enabled and disclosed.

## Deployment pattern

Start with one maintainable edge host and a small number of services. Avoid distributed complexity until measured requirements justify it. Containerisation may be used for reproducible deployment, with persistent data stored outside ephemeral containers.

## Decisions still to validate

- Hardware form factor and accelerator requirements.
- Model family, quantisation and licence suitability.
- Concurrent-user performance and latency.
- Storage growth and backup method.
- Network coverage and power budget at the pilot site.
- Identity model suitable for a school environment.
- Content moderation and human oversight approach.
