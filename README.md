# PROJECT NOMAD

**Community-owned sovereign AI infrastructure for offline-first education, local knowledge access and sustainable community networks.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Status: V0.5 prototype](https://img.shields.io/badge/status-V0.5%20prototype-blue.svg)](#project-status)

PROJECT NOMAD is an open-source public-interest initiative exploring how schools and communities can own, operate and maintain useful AI and digital knowledge services locally—even when internet connectivity is limited or unavailable.

The initial pilot is proposed for **schools and educational communities in Lagos State, Nigeria**. No pilot school, institutional partner or deployment is currently confirmed.

## Why NOMAD

Many educational and community organisations face a combination of unreliable connectivity, high recurring service costs, limited access to locally operated computing, and dependence on external platforms. NOMAD aims to make resilient digital infrastructure more accessible by placing essential services closer to the people who use and govern them.

The project is based on five principles:

- **Local-first:** Core services should continue to work without continuous internet access.
- **Community ownership:** Participating communities should have meaningful control over their infrastructure and its operation.
- **Open and reusable:** Software, deployment guidance and governance resources should be publicly accessible under clear licences.
- **Privacy and safety by design:** Collect as little personal data as possible, with special safeguards for school environments and children.
- **Maintainability:** Hardware, software and operational procedures should be understandable, repairable and supportable locally.

## Proposed system

| Component | Purpose |
|---|---|
| **NOMAD AI CORE** | Local AI model serving and inference management. |
| **NOMAD KNOWLEDGE** | Offline educational resources, document indexing and local knowledge retrieval. |
| **NOMAD NETWORK** | Local Wi-Fi/LAN access and service discovery. |
| **NOMAD ENERGY** | Renewable-energy and battery integration where appropriate. |
| **NOMAD GOVERNANCE** | Access control, privacy, community decision-making and maintenance practices. |

These are planned components, not claims of completed functionality.

## Initial Lagos pilot: proposed scope

The first field study will seek to identify one suitable school or educational community in Lagos State. The pilot will be co-designed with school leadership, teachers, learners and relevant community stakeholders.

Preliminary engineering hypotheses for evaluation—not deployment commitments—include:

- Up to 100 concurrent users in a first test configuration.
- Approximately 4 TB of local storage.
- Local AI inference and retrieval over approved content.
- Offline access through a local web application and wireless network.
- Power resilience appropriate to the selected site.
- Training and documented handover to local operators.

Actual capacity, hardware and energy requirements must be validated through workload tests and a site assessment.

## Architecture direction

The initial design is a small, modular system rather than a complex microservice platform:

1. A web portal / progressive web application for users.
2. A local gateway and API for service access.
3. A local AI runtime selected through model and hardware benchmarking.
4. A knowledge service for approved documents and resources.
5. Local persistent storage and database services.
6. Administrative controls, logging and recovery procedures.
7. Optional, controlled synchronisation when external connectivity is available.

A system must not silently send school or learner data to external AI providers. External connectivity and synchronisation should be explicit, configurable and documented.

## Technology direction

Candidate technologies may include:

- **Frontend:** React, Next.js and TypeScript.
- **API:** Python and FastAPI.
- **AI runtime:** llama.cpp or another locally deployable runtime chosen after evaluation.
- **Data:** PostgreSQL and local file/object storage.
- **Deployment:** Docker for reproducible installation.
- **Operations:** Linux, local networking, monitoring and backup tooling.

Technology choices remain provisional until a working prototype and hardware benchmarks justify them. Model weights, datasets and third-party packages retain their own licences and terms; the repository's Apache-2.0 licence does not relicense those materials.

## Privacy, safeguarding and responsible AI

The school pilot must be designed around privacy, safety and human oversight.

- Do not collect identifiable learner information unless it is demonstrably necessary and properly authorised.
- Do not use student data to train or fine-tune models by default.
- Do not deploy facial recognition, behavioural profiling or automated high-stakes decisions about learners.
- Use age-appropriate content controls and clear routes for reporting harmful or inaccurate outputs.
- Ensure teachers and authorised adults remain responsible for educational decisions.
- Complete appropriate privacy, safeguarding and security reviews before field testing.
- Obtain required institutional approvals, notices and consent before processing personal data.

NOMAD is an infrastructure and research project, not a substitute for professional teaching, medical advice or public services.

## Open development and governance

The project intends to publish reusable source code, technical documentation, deployment instructions, evaluation methods and community governance resources. Contributions should be transparent and reviewable.

The project will seek community input before deciding how local resources are selected, how infrastructure is administered, who can access services, and how the system is maintained or retired.

No school, university, government body, NGO or other institution is represented as a partner unless a collaboration is explicitly agreed and documented.

## Run the V0.3 prototype locally

### Requirements

- Node.js 22 or later and npm
- Python 3.12 or later
- Docker Engine and Docker Compose (optional)

### Start with Docker

From the repository root:

```bash
docker compose up --build
```

Then open:

- Web portal on the host: http://localhost:3000
- API health on the host: http://localhost:8000/health
- API search on the host: http://localhost:8000/api/knowledge/search?q=offline%20learning

For other devices on the same local network, open `http://<NOMAD-SERVER-LAN-IP>:3000`. The browser sends API requests to the same web origin; the NOMAD web container proxies them to the API over the private Docker network. The API port is bound to host loopback only and is not directly exposed to the LAN.

### Run services without Docker

Start the API:

```bash
cd backend
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In a second terminal, from the repository root:

```bash
npm install
npm run dev
```

Open http://localhost:3000. The frontend expects the API at http://localhost:8000 by default. Set `NEXT_PUBLIC_NOMAD_API_URL` before building if a different address is required.

### Configure the prototype operator token

Generate a strong random token on the NOMAD host, for example with `openssl rand -hex 32`. Add it to the private repository-root `.env` file as `NOMAD_OPERATOR_TOKEN=<generated-value>`. Never commit the real value or include it in screenshots. Restart the API container after changing it. If the variable is missing or shorter than 32 characters, operator access remains unavailable.

The protected endpoint is `GET /api/operator/status` and requires `Authorization: Bearer <token>`. The public network status endpoint remains informational and read-only. This prototype does not yet provide individual accounts, MFA, recovery, audit trails, granular roles, rate limiting or session revocation.

### Run backend tests

From the repository root:

```bash
cd backend
pytest -q
```

## Current prototype capabilities

V0.5 adds a fail-closed single-operator bearer-token gate for the read-only `/api/operator/status` endpoint. The API reads `NOMAD_OPERATOR_TOKEN`; tokens shorter than 32 characters are rejected as unconfigured. The browser keeps the entered token in page memory only. This is a bootstrap control, not multi-user identity or production-grade security. Do not expose the prototype to untrusted networks. See [operator access control](docs/architecture/operator-access-control.md).

V0.4 adds a local infrastructure status endpoint and a basic operator status view for the API, optional local AI, knowledge index, configured network mode and external-sync setting. It deliberately does not scan the LAN, administer Wi-Fi clients or expose device addresses.

V0.2 adds an optional Ollama adapter for local model status and source-grounded answers. V0.3 adds an optional local semantic knowledge index using Ollama embeddings and SQLite, while retaining lexical search as a fallback. Both AI generation and embeddings are disabled by default. See the [local AI runtime design](docs/architecture/local-ai-runtime.md) and [semantic knowledge engine design](docs/architecture/semantic-knowledge-engine.md).

To enable the optional local runtime with Docker, set `NOMAD_AI_PROVIDER=ollama` in your environment and run:

```bash
docker compose --profile ai up --build -d
docker compose exec nomad-ollama ollama pull llama3.2:3b
```

Then set `NOMAD_OLLAMA_MODEL` to the installed model name if you chose a different model. Check `http://localhost:3000/api/ai/status` and use `POST /api/ai/answer` with a JSON body such as `{"question":"What is offline learning?"}`. Model download requires internet access initially; once downloaded, inference can run locally. Review model licence, hardware requirements and safeguarding suitability before use.

### Optional semantic retrieval

Semantic retrieval remains disabled unless explicitly configured. Start the optional Ollama service, pull an embedding model you have evaluated, then configure:

```bash
NOMAD_EMBEDDINGS_PROVIDER=ollama
NOMAD_OLLAMA_EMBED_MODEL=nomic-embed-text
NOMAD_SEMANTIC_MIN_SCORE=0.35
```

With these values saved in the repository-root .env file, start the optional local runtime and download the embedding model:

```bash
docker compose --profile ai up --build -d
docker compose exec nomad-ollama ollama pull nomic-embed-text
```

Build or refresh the local SQLite index inside the API container:

```bash
docker compose exec nomad-api python -m app.index_knowledge
```

Check `/api/knowledge/index/status`. The search endpoint uses local semantic retrieval when the index is ready and falls back to lexical search if semantic retrieval is disabled or unavailable. The indexer is an operator command, not a public API endpoint. Do not index identifiable learner data.

## Project status

**Current stage: V0.5 operator access-control foundation in development; research, design and partner discovery continue.**

- [ ] Confirm a Lagos pilot school or educational community.
- [ ] Recruit research, technical and community collaborators.
- [ ] Conduct community needs assessment and site survey.
- [ ] Validate data protection, safeguarding and governance requirements.
- [ ] Evaluate semantic retrieval quality, multilingual coverage and source-grounding.
- [ ] Add access controls and operational safeguards before any multi-user field test.
- [ ] Build and benchmark the first offline knowledge and local inference prototype.
- [ ] Benchmark performance, reliability, energy use and recovery.
- [ ] Conduct a controlled pilot only after approvals.
- [ ] Publish deployment, maintenance and evaluation documentation.

Milestones and performance targets will be revised as evidence is gathered. The project does not currently claim an operational deployment, confirmed partners or active users.

## Contributing

Early contributions are welcome in architecture review, local AI evaluation, offline-first design, networking, energy systems, privacy engineering, accessibility, educational content governance and documentation.

Before contributing:

1. Open an issue describing the proposal or problem.
2. Avoid submitting personal, confidential or sensitive school/learner data.
3. Follow the project contribution guidance as it is established.
4. Include tests and documentation for changes where applicable.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution process. Use GitHub Issues for discussion.

## Repository structure

The repository will evolve as implementation begins. Planned areas include:

```text
project-nomad/
├── apps/
│   └── web-portal/
├── services/
│   ├── ai-core/
│   ├── knowledge-engine/
│   ├── network-manager/
│   └── identity-access/
├── infrastructure/
│   ├── docker/
│   ├── networking/
│   └── monitoring/
├── hardware/
│   ├── bom/
│   └── energy/
├── docs/
│   ├── architecture/
│   ├── deployment/
│   ├── governance/
│   └── safeguarding/
├── research/
└── tests/
```

Directories and components will be added when their initial scope is agreed; this is a target structure, not a claim that they are already implemented.

## Licence

The repository's original software and documentation are intended to be made available under the [Apache License 2.0](LICENSE), unless a file states otherwise. Third-party models, datasets, media and dependencies may have separate licences and must be reviewed individually.

## Contact

**Project lead:** John Ebster-Davids  
**Email:** dragoxprotocol@proton.me  
**LinkedIn:** https://www.linkedin.com/in/john-ebster-davids-807aaa293/  
**Project website:** https://dragoxprotocol.carrd.co/

---

*Community-owned intelligence. Open infrastructure. Sustainable digital independence.*
