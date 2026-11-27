# V0.7 — Hardware, network, AI and energy benchmarking plan

## Purpose

V0.7 introduces repeatable measurement tools and a disciplined evidence record. It does **not** certify hardware, promise concurrent-user capacity, validate a solar design, or claim that a field pilot has taken place.

## Measurement workstreams

1. **API and portal:** run the opt-in client benchmark against `/health`, knowledge search and other explicitly selected endpoints. Record client location, wired/Wi-Fi connection, request count, concurrency, warm-up, timeout, status codes, throughput and latency percentiles.
2. **Knowledge retrieval:** measure corpus size, document count, chunk count, index build duration, embedding model/version, indexing failures and query latency. Compare lexical fallback and semantic retrieval against a reviewed question set; report relevance separately from speed.
3. **Local AI inference:** record runtime and version, model identifier and quantisation, prompt/input/output token counts where available, cold-start time, time-to-first-token, total response time, generation rate, concurrency, memory and thermal behaviour. Do not infer performance from model names.
4. **Storage:** measure sequential and random read/write performance, usable capacity, filesystem, device type, encryption and backup/restore duration. Protect real learner data; use synthetic fixtures.
5. **LAN:** measure client-to-gateway latency, packet loss, throughput and performance at progressively increasing client counts. Use a controlled test network and authorised devices only. No network scanning or undisclosed client inventory.
6. **Energy:** log real watt-hours at the AC/DC boundary, load profile, battery state of charge, solar input, weather, downtime and ambient temperature. Compare measured energy with the estimate from `scripts/energy_budget.py`.

## Standard test sequence

- Record the completed hardware inventory before testing.
- Document software commit, operating system, runtime, model and configuration.
- Use synthetic, non-personal test content and an isolated test LAN.
- Run a low-load baseline, then increase one variable at a time.
- Repeat each scenario at least three times; report median and range, not only the best run.
- Capture failures, throttling, thermal events, restarts and recovery behaviour.
- Preserve raw JSON/CSV outputs with timestamps and a short interpretation.
- Do not extrapolate a short test into a 100- or 200-user deployment claim.

## Repository tools

- `python scripts/api_benchmark.py --url http://127.0.0.1:3000/health --requests 30 --concurrency 2 --output results/api-health.json`
- `python scripts/energy_budget.py --loads-json '[{"name":"server","watts":120,"hours_per_day":24},{"name":"access-point","watts":12,"hours_per_day":24}]' --voltage 24 --sun-hours 4`

Run these from the repository root. The API tool makes real requests to the supplied target; start with a local instance and a small workload. It is not a stress-test tool. Do not run aggressive loads against a shared or production system.

## Required evidence before hardware recommendations

- Named device models and verified component specifications.
- Measured idle, typical and peak power draw.
- Measured API, retrieval and inference latency under documented workloads.
- Thermal and sustained-load results.
- LAN coverage and concurrent-client measurements at the intended site.
- Storage endurance, backup and restore evidence.
- Solar resource/site survey, measured load profile, autonomy requirement, battery chemistry and protection design reviewed by a qualified installer.
- Safeguarding, privacy, security and institutional approvals before any school deployment.

## Current evidence status

No target-site hardware, school LAN, solar installation or community pilot has been measured or validated by this repository work. The user and project team must collect field evidence before setting procurement specifications or confirming capacity.
