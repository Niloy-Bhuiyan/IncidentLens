PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS investigations (id TEXT PRIMARY KEY, question TEXT NOT NULL, status TEXT NOT NULL, report_json TEXT, created_at TEXT NOT NULL, completed_at TEXT);
CREATE TABLE IF NOT EXISTS evidence_sources (id TEXT PRIMARY KEY, source_id TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL, content_hash TEXT NOT NULL UNIQUE, source_path TEXT NOT NULL, metadata_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_evidence_kind ON evidence_sources(kind);
CREATE TABLE IF NOT EXISTS evidence_chunks (id TEXT PRIMARY KEY, evidence_id TEXT NOT NULL REFERENCES evidence_sources(id) ON DELETE CASCADE, chunk_index INTEGER NOT NULL, content TEXT NOT NULL, metadata_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_chunks_evidence ON evidence_chunks(evidence_id);
CREATE TABLE IF NOT EXISTS entities (id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, label TEXT NOT NULL, metadata_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence_relations (id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, target_id TEXT NOT NULL, relation_type TEXT NOT NULL, weight REAL NOT NULL, provenance TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_relation_source ON evidence_relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relation_target ON evidence_relations(target_id);
CREATE TABLE IF NOT EXISTS retrieval_runs (id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE, query TEXT NOT NULL, strategy TEXT NOT NULL, duration_ms REAL NOT NULL, ranked_ids_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS agent_runs (id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE, provider TEXT NOT NULL, prompt_version TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS agent_steps (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE, node TEXT NOT NULL, status TEXT NOT NULL, duration_ms REAL NOT NULL, summary TEXT NOT NULL, step_order INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE, text TEXT NOT NULL, confidence REAL NOT NULL, verification_status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS claim_evidence (claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE, evidence_id TEXT NOT NULL REFERENCES evidence_sources(id) ON DELETE CASCADE, relationship TEXT NOT NULL, PRIMARY KEY (claim_id, evidence_id));
CREATE TABLE IF NOT EXISTS evaluation_runs (id TEXT PRIMARY KEY, dataset_version TEXT NOT NULL, configuration TEXT NOT NULL, metrics_json TEXT NOT NULL, commit_sha TEXT, created_at TEXT NOT NULL);

