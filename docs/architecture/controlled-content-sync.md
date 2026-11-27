# Controlled Offline Content Synchronisation — V0.6

## Scope

V0.6 implements a local, operator-triggered staged-bundle import. It does not fetch internet URLs, poll external repositories or run background synchronisation jobs. An operator stages a bundle on the NOMAD host, reviews a preview, then explicitly imports it using the authenticated API.

## Bundle format

Each bundle is a directory under `NOMAD_SYNC_INBOX` and contains `manifest.json` plus the declared source files. The manifest uses version `1`, repeats the bundle directory identifier, and declares a list of source records with `source_id`, `file` and `sha256`.

Only `.md` and `.txt` UTF-8 files are accepted. Filenames must be simple filenames without path components. The default per-file size limit is 2 MB and the manifest is limited to 128 KB. A bundle can contain at most 100 sources.

## Approval and integrity controls

- Source IDs must be present in `NOMAD_SYNC_ALLOWED_SOURCE_IDS`.
- The operator must authenticate and call preview before choosing import.
- SHA-256 is checked against each staged file before any content is written.
- Symlinks, path traversal, unsupported file types, binary/NUL content and oversized files are rejected.
- Imports use deterministic hash-derived names and are idempotent.
- A failed multi-file import attempts to remove files created during that import.

The allowlist is an operator configuration, not cryptographic publisher identity. SHA-256 proves consistency with the manifest, not who authored it. If an attacker can replace both staged content and manifest, hashes alone do not establish authenticity. Review publisher identity and content before allowing a source ID.

## API

- `POST /api/operator/sync/preview` — validates the staged bundle without writing knowledge files.
- `POST /api/operator/sync/import` — revalidates and imports the approved bundle.

Both endpoints require the V0.5 operator Bearer token. They are unavailable when operator authentication is not configured.

## After import

The lexical knowledge search reads the imported Markdown/text files from the configured knowledge directory. If semantic retrieval is enabled, an operator must rebuild the local index using `python -m app.index_knowledge`.

## Limitations and next gates

This release has no remote fetching, signed manifests, trusted publisher key registry, content moderation, malware scanning, background scheduling, deletion/reconciliation protocol, conflict resolution for mutable source records, or rollback UI. It is a controlled local ingest foundation, not a complete synchronisation service.

Before a school/community deployment, add publisher signatures or another authenticated provenance mechanism, content review workflow, malware scanning appropriate to the deployment, immutable import audit records, explicit rollback and removal controls, backup/recovery tests, and independent security review.
