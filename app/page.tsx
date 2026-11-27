"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

type Health = {
  status: string;
  service: string;
  mode: string;
};

type NetworkStatus = {
  network_mode: string; connectivity: string; external_sync_enabled: boolean;
  device_discovery: string; services: { api: string; local_ai: string; knowledge_index: string };
};

type SearchResult = {
  title: string;
  source: string;
  excerpt: string;
  score: number;
};

export default function Home() {
  const [health, setHealth] = useState<Health | null>(null);
  const [network, setNetwork] = useState<NetworkStatus | null>(null);
  const [query, setQuery] = useState("");
  const [operatorToken, setOperatorToken] = useState("");
  const [operatorMessage, setOperatorMessage] = useState("Operator access requires a server-configured token.");
  const [operatorAuthenticated, setOperatorAuthenticated] = useState(false);
  const [operatorLoading, setOperatorLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(
    "Search the local demonstration knowledge library. No cloud AI is used."
  );

  useEffect(() => {
    let active = true;
    fetch("/api/network/status")
      .then((response) => { if (!response.ok) throw new Error("Network status unavailable"); return response.json(); })
      .then((data: NetworkStatus) => { if (active) setNetwork(data); })
      .catch(() => { if (active) setNetwork(null); });
    fetch("/health")
      .then((response) => {
        if (!response.ok) throw new Error("Backend unavailable");
        return response.json();
      })
      .then((data: Health) => {
        if (active) setHealth(data);
      })
      .catch(() => {
        if (active) setHealth(null);
      });
    return () => {
      active = false;
    };
  }, []);

  async function handleOperatorAccess(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!operatorToken.trim()) { setOperatorMessage("Enter the operator token configured by the system administrator."); return; }
    setOperatorLoading(true); setOperatorMessage("Checking operator credentials…");
    try {
      const response = await fetch("/api/operator/status", { headers: { Authorization: "Bearer " + operatorToken.trim() } });
      if (!response.ok) throw new Error(response.status === 503 ? "Operator access is not configured on this server." : "Authentication failed. Check the token and try again.");
      const data = await response.json(); setOperatorAuthenticated(true);
      setOperatorMessage("Authenticated as " + data.operator.role + ". This prototype provides read-only status access.");
    } catch (error) {
      setOperatorAuthenticated(false); setOperatorMessage(error instanceof Error ? error.message : "Operator authentication failed.");
    } finally { setOperatorLoading(false); }
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleaned = query.trim();
    if (cleaned.length < 2) {
      setMessage("Enter at least two characters to search.");
      setResults([]);
      return;
    }

    setLoading(true);
    setMessage("Searching the local knowledge library…");
    try {
      const response = await fetch(
        `/api/knowledge/search?q=${encodeURIComponent(cleaned)}&limit=8`
      );
      if (!response.ok) throw new Error("The local search service returned an error.");
      const data = await response.json();
      setResults(data.results ?? []);
      setMessage(
        data.results?.length
          ? `Found ${data.results.length} local result(s).`
          : "No matching local documents were found."
      );
    } catch {
      setResults([]);
      setMessage(
        "Cannot reach the NOMAD backend. Start the local services and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <nav className="topbar">
        <Link className="brand" href="/" aria-label="PROJECT NOMAD home">
          <span className="brand-mark">N</span>
          <span>PROJECT <strong>NOMAD</strong></span>
        </Link>
        <span className="version">PROTOTYPE V0.4</span>
      </nav>

      <section className="hero">
        <div className="eyebrow"><span className="pulse" /> LOCAL-FIRST COMMUNITY INFRASTRUCTURE</div>
        <h1>Knowledge should work<br /><em>where people are.</em></h1>
        <p className="intro">
          A community-owned foundation for offline knowledge access and, as the
          platform develops, locally operated AI services.
        </p>
        <div className="status-row">
          <span className={health ? "status-dot online" : "status-dot"} />
          <span>{health ? "Local backend connected" : "Backend not connected"}</span>
          <span className="status-divider">/</span>
          <span>External AI: not configured</span>
        </div>
      </section>

      <section className="workspace" aria-labelledby="network-title">
        <div className="section-heading"><div><div className="eyebrow muted">NOMAD NETWORK</div><h2 id="network-title">Local infrastructure status</h2></div><span className="local-tag">OPERATOR VIEW</span></div>
        {network ? (
          <div className="principle-grid">
            <div><span>NETWORK MODE</span><h3>{network.network_mode.toUpperCase()}</h3><p>Local-first network configuration.</p></div>
            <div><span>API SERVICE</span><h3>{network.services.api}</h3><p>Local gateway service health.</p></div>
            <div><span>LOCAL AI</span><h3>{network.services.local_ai}</h3><p>Optional local inference runtime.</p></div>
            <div><span>KNOWLEDGE INDEX</span><h3>{network.services.knowledge_index}</h3><p>Local retrieval index status.</p></div>
            <div><span>DEVICE DISCOVERY</span><h3>{network.device_discovery}</h3><p>No automatic network scanning is performed.</p></div>
            <div><span>EXTERNAL SYNC</span><h3>{network.external_sync_enabled ? "ENABLED" : "DISABLED"}</h3><p>External synchronisation is opt-in.</p></div>
          </div>
        ) : <p className="message">Network status service is not reachable.</p>}
      </section>

      <section className="workspace" aria-labelledby="operator-title">
        <div className="section-heading"><div><div className="eyebrow muted">NOMAD GOVERNANCE</div><h2 id="operator-title">Operator access</h2></div><span className="local-tag">{operatorAuthenticated ? "AUTHENTICATED" : "PROTECTED"}</span></div>
        <form className="search-form" onSubmit={handleOperatorAccess}>
          <label className="sr-only" htmlFor="operator-token">Operator bearer token</label>
          <input id="operator-token" type="password" autoComplete="off" value={operatorToken} onChange={(event) => setOperatorToken(event.target.value)} placeholder="Enter server-configured operator token" />
          <button type="submit" disabled={operatorLoading}>{operatorLoading ? "Checking…" : "Authenticate"}</button>
        </form>
        <p className="message" role="status">{operatorMessage}</p>
        <p className="message">The token remains in this page’s memory only; it is not written to browser storage. This is a single-operator bootstrap prototype, not multi-user account management.</p>
      </section>

      <section className="workspace" aria-labelledby="search-title">
        <div className="section-heading">
          <div>
            <div className="eyebrow muted">NOMAD KNOWLEDGE</div>
            <h2 id="search-title">Search local knowledge</h2>
          </div>
          <span className="local-tag">LOCAL SEARCH</span>
        </div>
        <form className="search-form" onSubmit={handleSearch}>
          <label className="sr-only" htmlFor="query">Search the knowledge library</label>
          <input
            id="query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try: community networks, solar energy, education…"
            autoComplete="off"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Searching…" : "Search"}
          </button>
        </form>
        <p className="message" role="status">{message}</p>

        {results.length > 0 && (
          <div className="results">
            {results.map((result) => (
              <article className="result-card" key={result.source}>
                <div className="result-meta">
                  <span>LOCAL DOCUMENT</span>
                  <span>{result.source}</span>
                </div>
                <h3>{result.title}</h3>
                <p>{result.excerpt}</p>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="principles">
        <div className="eyebrow muted">DESIGNED AROUND FIVE PRINCIPLES</div>
        <div className="principle-grid">
          <div><span>01</span><h3>Local-first</h3><p>Core services designed to operate on a local network.</p></div>
          <div><span>02</span><h3>Community-owned</h3><p>Infrastructure governed with the people who use it.</p></div>
          <div><span>03</span><h3>Open</h3><p>Reusable software, documentation and deployment guidance.</p></div>
          <div><span>04</span><h3>Privacy-led</h3><p>Data minimisation and safeguards from the start.</p></div>
          <div><span>05</span><h3>Maintainable</h3><p>Systems local operators can understand and support.</p></div>
        </div>
      </section>

      <footer>
        <span>PROJECT NOMAD · LAGOS STATE PILOT PROPOSAL</span>
        <span>Research and prototype stage · No deployment claimed</span>
      </footer>
    </main>
  );
}
