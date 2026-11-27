# NOMAD V0.2 — Optional local AI runtime

## Objective

Add a locally hosted, opt-in language-model capability without making the core portal dependent on a model, internet access or a hosted AI provider. The existing local lexical search remains available independently.

## Current implementation boundary

- The API supports an optional Ollama-compatible local runtime.
- NOMAD_AI_PROVIDER defaults to disabled; no model is contacted in this state.
- When enabled, the API checks the configured local Ollama endpoint and model.
- The answer endpoint retrieves matching local Markdown/text excerpts and sends only those excerpts plus the question to the configured local runtime.
- The response returns source identifiers and instructs the model to cite excerpts as [1], [2].
- If lexical retrieval finds no local source, the API returns a fixed insufficient-evidence response and does not call the model.
- Retrieved documents are explicitly treated as untrusted reference data in the model prompt; prompt-injection resistance is a mitigation, not a guarantee.
- No hosted model provider, external telemetry or student-data training path is implemented.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| NOMAD_AI_PROVIDER | disabled | Set to ollama to enable local inference |
| NOMAD_OLLAMA_BASE_URL | http://127.0.0.1:11434 | Local Ollama API base URL |
| NOMAD_OLLAMA_MODEL | llama3.2:3b | Model name expected to be installed locally |
| NOMAD_AI_TIMEOUT_SECONDS | 45 | Generation request timeout |

For Docker deployments, set NOMAD_OLLAMA_BASE_URL to the Ollama service's private network address. Do not expose the Ollama port to the public internet. The model name is a configurable starting default, not a hardware recommendation; benchmark candidate models on the target server before selecting one for a school deployment.

## API

- GET /api/ai/status reports whether local AI is disabled, reachable and has the configured model installed.
- POST /api/ai/answer accepts a question and optional source limit, then returns a locally generated answer plus local document paths used as context.

The answer endpoint returns HTTP 503 when AI is disabled, the runtime is unavailable, the configured model is missing or generation fails. This avoids silently falling back to a remote provider.

## Safeguards and limitations

- Retrieval is still lexical, not semantic/vector retrieval.
- Model citations are generated text and are not independently verified; clients should display the returned source list alongside the answer.
- Prompt-injection instructions in source documents may still influence model behaviour despite defensive prompting; this requires adversarial evaluation.
- This is not a substitute for teacher review, safeguarding review or factual verification.
- Do not submit identifiable learner data. Do not use the endpoint for learner profiling, grading or high-stakes decisions.
- The runtime is not enabled by default. Administrators must deliberately configure it and manage model files and licences.
- Authentication, role-based access, rate limiting, content moderation, model evaluation and production monitoring remain future work before a school pilot.

## Next engineering gates

1. Benchmark model quality, latency, memory and energy consumption on candidate hardware.
2. Add deterministic source-grounding evaluation and adversarial prompt tests.
3. Add administrator authentication and usage controls before multi-user deployment.
4. Evaluate semantic retrieval only after a maintainable offline embedding/index strategy is selected.
5. Conduct privacy, safeguarding and security review before any field test.
