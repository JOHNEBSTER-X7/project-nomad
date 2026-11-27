"use client";

import { FormEvent, useEffect, useState } from "react";

type Health = {
  status: string;
  service: string;
  mode: string;
};

type SearchResult = {
  title: string;
  source: string;
  excerpt: string;
  score: number;
};

const API_BASE =
  process.env.NEXT_PUBLIC_NOMAD_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState<Health | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(
    "Search the local demonstration knowledge library. No cloud AI is used."
  );

  useEffect(() => {
    let active = true;
    fetch(`${API_BASE}/health`)
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
        `${API_BASE}/api/knowledge/search?q=${encodeURIComponent(cleaned)}&limit=8`
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
        <a className="brand" href="/" aria-label="PROJECT NOMAD home">
          <span className="brand-mark">N</span>
          <span>PROJECT <strong>NOMAD</strong></span>
        </a>
        <span className="version">PROTOTYPE V0.1</span>
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
