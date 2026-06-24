import React, { useEffect, useMemo, useState } from "react";

/* ============================================================================
   API LAYER  —  this is the only block you touch to wire up your FastAPI app.
   ========================================================================== */
const API_BASE =
  (typeof process !== "undefined" &&
    process.env &&
    process.env.REACT_APP_API_URL) ||
  "http://localhost:8000";

const ENDPOINTS = {
  prediction: "/predict/latest",
  standings: "/data/standings",
  modelInfo: "/info",
};

async function safeGet(path, fallback) {
  try {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { data: await res.json(), live: true };
  } catch (e) {
    return { data: fallback, live: false };
  }
}

function normalizePrediction(raw) {
  return {
    race: raw.race ?? raw.grand_prix ?? "Grand Prix",
    circuit: raw.circuit ?? raw.track ?? "",
    season: raw.season ?? new Date().getFullYear(),
    round: raw.round ?? raw.round_number ?? "—",
    predictedAt: raw.predicted_at ?? raw.timestamp ?? null,
    drivers: (raw.predictions ?? raw.drivers ?? raw.results ?? []).map((d, i) => ({
      pos: d.position ?? d.predicted_position ?? i + 1,
      code: d.driver_code ?? d.code ?? d.abbreviation ?? "",
      name: d.driver ?? d.driver_name ?? d.name ?? "",
      team: d.team ?? d.constructor ?? "",
      win: num(d.win_probability ?? d.win_prob ?? d.p_win),
      podium: num(d.podium_probability ?? d.podium_prob ?? d.p_podium),
      points: num(d.points_probability ?? d.points_prob ?? d.p_points),
    })),
  };
}

const num = (v) => (typeof v === "number" ? v : v != null ? Number(v) : null);

/* ============================================================================
   STATIC DATA  —  team colors + mock fallback (Abu Dhabi 2025)
   ========================================================================== */
const TEAM = {
  "Red Bull Racing": "#3671C6",
  Ferrari: "#E8002D",
  McLaren: "#FF8000",
  Mercedes: "#27F4D2",
  "Aston Martin": "#229971",
  Alpine: "#0093CC",
  Williams: "#1868DB",
  "Racing Bulls": "#6692FF",
  Haas: "#B6BABD",
  "Kick Sauber": "#52E252",
};

const teamColor = (t) => TEAM[t] || "#8A8A96";

const MOCK_PREDICTION = {
  race: "Abu Dhabi Grand Prix",
  circuit: "Yas Marina Circuit",
  season: 2025,
  round: 24,
  predicted_at: "2025-12-05T14:00:00Z",
  predictions: [
    { position: 1, driver_code: "NOR", driver: "Lando Norris", team: "McLaren", win_probability: 0.34, podium_probability: 0.71, points_probability: 0.96 },
    { position: 2, driver_code: "VER", driver: "Max Verstappen", team: "Red Bull Racing", win_probability: 0.29, podium_probability: 0.66, points_probability: 0.95 },
    { position: 3, driver_code: "PIA", driver: "Oscar Piastri", team: "McLaren", win_probability: 0.18, podium_probability: 0.58, points_probability: 0.93 },
    { position: 4, driver_code: "LEC", driver: "Charles Leclerc", team: "Ferrari", win_probability: 0.08, podium_probability: 0.41, points_probability: 0.9 },
    { position: 5, driver_code: "RUS", driver: "George Russell", team: "Mercedes", win_probability: 0.05, podium_probability: 0.33, points_probability: 0.88 },
    { position: 6, driver_code: "HAM", driver: "Lewis Hamilton", team: "Ferrari", win_probability: 0.03, podium_probability: 0.24, points_probability: 0.83 },
    { position: 7, driver_code: "ANT", driver: "Kimi Antonelli", team: "Mercedes", win_probability: 0.01, podium_probability: 0.14, points_probability: 0.74 },
    { position: 8, driver_code: "SAI", driver: "Carlos Sainz", team: "Williams", win_probability: 0.01, podium_probability: 0.09, points_probability: 0.61 },
    { position: 9, driver_code: "ALB", driver: "Alex Albon", team: "Williams", win_probability: 0.0, podium_probability: 0.05, points_probability: 0.52 },
    { position: 10, driver_code: "TSU", driver: "Yuki Tsunoda", team: "Red Bull Racing", win_probability: 0.0, podium_probability: 0.04, points_probability: 0.44 },
    { position: 11, driver_code: "GAS", driver: "Pierre Gasly", team: "Alpine", win_probability: 0.0, podium_probability: 0.02, points_probability: 0.35 },
    { position: 12, driver_code: "HAD", driver: "Isack Hadjar", team: "Racing Bulls", win_probability: 0.0, podium_probability: 0.02, points_probability: 0.31 },
    { position: 13, driver_code: "ALO", driver: "Fernando Alonso", team: "Aston Martin", win_probability: 0.0, podium_probability: 0.01, points_probability: 0.27 },
    { position: 14, driver_code: "LAW", driver: "Liam Lawson", team: "Racing Bulls", win_probability: 0.0, podium_probability: 0.01, points_probability: 0.22 },
    { position: 15, driver_code: "BEA", driver: "Oliver Bearman", team: "Haas", win_probability: 0.0, podium_probability: 0.01, points_probability: 0.18 },
    { position: 16, driver_code: "HUL", driver: "Nico Hülkenberg", team: "Kick Sauber", win_probability: 0.0, podium_probability: 0.0, points_probability: 0.15 },
    { position: 17, driver_code: "STR", driver: "Lance Stroll", team: "Aston Martin", win_probability: 0.0, podium_probability: 0.0, points_probability: 0.12 },
    { position: 18, driver_code: "OCO", driver: "Esteban Ocon", team: "Haas", win_probability: 0.0, podium_probability: 0.0, points_probability: 0.1 },
    { position: 19, driver_code: "BOR", driver: "Gabriel Bortoleto", team: "Kick Sauber", win_probability: 0.0, podium_probability: 0.0, points_probability: 0.08 },
    { position: 20, driver_code: "COL", driver: "Franco Colapinto", team: "Alpine", win_probability: 0.0, podium_probability: 0.0, points_probability: 0.06 },
  ],
};

const MOCK_MODEL = {
  model: "GradientBoosting + EnsembleStacker",
  version: "v3.2.1",
  trained_on: "2018–2025 (172 races)",
  accuracy: 0.83,
  podium_accuracy: 0.71,
  features: 47,
};

const MOCK_STANDINGS = {
  drivers: [
    { pos: 1, code: "NOR", name: "Lando Norris", team: "McLaren", points: 408 },
    { pos: 2, code: "VER", name: "Max Verstappen", team: "Red Bull Racing", points: 396 },
    { pos: 3, code: "PIA", name: "Oscar Piastri", team: "McLaren", points: 372 },
    { pos: 4, code: "LEC", name: "Charles Leclerc", team: "Ferrari", points: 251 },
    { pos: 5, code: "RUS", name: "George Russell", team: "Mercedes", points: 244 },
    { pos: 6, code: "HAM", name: "Lewis Hamilton", team: "Ferrari", points: 188 },
  ],
  constructors: [
    { pos: 1, name: "McLaren", points: 780 },
    { pos: 2, name: "Ferrari", points: 439 },
    { pos: 3, name: "Red Bull Racing", points: 421 },
    { pos: 4, name: "Mercedes", points: 398 },
    { pos: 5, name: "Williams", points: 121 },
  ],
};

/* ============================================================================
   COMPONENT
   ========================================================================== */
const pct = (v) => (v == null ? "—" : `${(v * 100).toFixed(v >= 0.1 ? 1 : 0)}%`);

export default function App() {
  const [tab, setTab] = useState("prediction");
  const [pred, setPred] = useState(null);
  const [model, setModel] = useState(MOCK_MODEL);
  const [standings, setStandings] = useState(MOCK_STANDINGS);
  const [live, setLive] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      const p = await safeGet(ENDPOINTS.prediction, MOCK_PREDICTION);
      const m = await safeGet(ENDPOINTS.modelInfo, MOCK_MODEL);
      const s = await safeGet(ENDPOINTS.standings, MOCK_STANDINGS);
      if (!alive) return;
      setPred(normalizePrediction(p.data));
      setModel(m.data);
      setStandings(s.data);
      setLive(p.live);
    })();
    const t = setTimeout(() => setMounted(true), 60);
    return () => {
      alive = false;
      clearTimeout(t);
    };
  }, []);

  const podium = useMemo(() => (pred ? pred.drivers.slice(0, 3) : []), [pred]);

  return (
    <div className="f1">
      <style>{CSS}</style>

      {/* ── FIX 1 & 2: renamed .bar → .topbar to avoid class collision with
           the probability bar inside .row__conf. Also added grid-area:race
           to .topbar__race so the header lays out correctly. ── */}
      <header className="topbar">
        <div className="wordmark">
          <span className="wordmark__tick" />
          <span className="wordmark__text">
            F1<span className="wordmark__slash">//</span>PREDICT
          </span>
        </div>
        <div className="topbar__race">
          {pred ? (
            <>
              <span className="topbar__gp">{pred.race}</span>
              <span className="topbar__circuit">
                {pred.circuit} · Round {pred.round} · {pred.season}
              </span>
            </>
          ) : (
            <span className="topbar__gp">Loading classification…</span>
          )}
        </div>
        <div className={`status ${live ? "status--live" : "status--mock"}`}>
          <span className="status__dot" />
          {live ? "LIVE MODEL" : "DEMO DATA"}
        </div>
      </header>

      <nav className="tabs">
        {[
          ["prediction", "Race Prediction"],
          ["standings", "Standings"],
          ["model", "Model"],
        ].map(([id, label]) => (
          <button
            key={id}
            className={`tab ${tab === id ? "tab--on" : ""}`}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </nav>

      {tab === "prediction" && pred && (
        <main className="view">
          {/* PODIUM */}
          <section className="podium">
            <p className="eyebrow">Predicted podium</p>
            <div className="podium__stage">
              {[podium[1], podium[0], podium[2]].map((d, i) =>
                d ? (
                  <PodiumStep
                    key={d.code}
                    d={d}
                    place={d.pos}
                    rank={["silver", "gold", "bronze"][i]}
                    mounted={mounted}
                  />
                ) : null
              )}
            </div>
          </section>

          <div className="split">
            {/* TIMING TOWER */}
            <section className="tower">
              <div className="tower__head">
                <p className="eyebrow">Predicted classification</p>
                <span className="tower__legend">Win&nbsp;probability</span>
              </div>
              <ol className="grid">
                {pred.drivers.map((d, i) => (
                  <li
                    key={d.code + d.pos}
                    className="row"
                    style={{
                      animationDelay: `${i * 32}ms`,
                      "--team": teamColor(d.team),
                    }}
                  >
                    <span className="row__bar" />
                    <span className="row__pos">{String(d.pos).padStart(2, "0")}</span>
                    <span className="row__code">{d.code}</span>
                    <span className="row__name">
                      {d.name}
                      <em className="row__team">{d.team}</em>
                    </span>
                    <span className="row__conf">
                      {/* FIX 2: renamed to .probbar so it never clashes with .topbar */}
                      <span className="probbar">
                        <span
                          className="probbar__fill"
                          style={{ width: mounted ? `${(d.win || 0) * 100}%` : 0 }}
                        />
                      </span>
                      <b>{pct(d.win)}</b>
                    </span>
                  </li>
                ))}
              </ol>
            </section>

            {/* RIGHT RAIL */}
            <aside className="rail">
              <div className="card">
                <p className="eyebrow">Model confidence</p>
                <div className="gauge">
                  <span className="gauge__num">{pct(model.accuracy ?? 0)}</span>
                  <span className="gauge__lbl">finish-order accuracy</span>
                </div>
                <div className="meta">
                  <Meta k="Podium acc." v={pct(model.podium_accuracy ?? 0)} />
                  <Meta k="Model" v={model.version ?? "—"} />
                  <Meta k="Features" v={model.features ?? "—"} />
                </div>
              </div>
              <div className="card">
                <p className="eyebrow">Confidence read</p>
                <ul className="legend">
                  <li><span className="legend__sw" style={{ background: "#52E252" }} />High — likely to finish ahead</li>
                  <li><span className="legend__sw" style={{ background: "#FFC400" }} />Medium — grid-dependent</li>
                  <li><span className="legend__sw" style={{ background: "#8A8A96" }} />Low — high variance</li>
                </ul>
                {pred.predictedAt && (
                  <p className="rail__ts">
                    Generated {new Date(pred.predictedAt).toLocaleString()}
                  </p>
                )}
              </div>
            </aside>
          </div>
        </main>
      )}

      {tab === "standings" && (
        <main className="view view--standings">
          <section className="card">
            <p className="eyebrow">Drivers' championship</p>
            <table className="table">
              <tbody>
                {(standings.drivers || []).map((d) => (
                  <tr key={d.code} style={{ "--team": teamColor(d.team) }}>
                    <td className="table__pos">{d.pos}</td>
                    <td className="table__bar"><span /></td>
                    <td className="table__name">{d.name}<em>{d.team}</em></td>
                    <td className="table__pts">{d.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          <section className="card">
            <p className="eyebrow">Constructors' championship</p>
            <table className="table">
              <tbody>
                {(standings.constructors || []).map((c) => (
                  <tr key={c.name} style={{ "--team": teamColor(c.name) }}>
                    <td className="table__pos">{c.pos}</td>
                    <td className="table__bar"><span /></td>
                    <td className="table__name">{c.name}</td>
                    <td className="table__pts">{c.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </main>
      )}

      {tab === "model" && (
        <main className="view view--model">
          <section className="card card--wide">
            <p className="eyebrow">Inference pipeline</p>
            <h2 className="model__name">{model.model ?? "—"}</h2>
            <div className="model__grid">
              <Meta k="Version" v={model.version ?? "—"} big />
              <Meta k="Finish accuracy" v={pct(model.accuracy ?? 0)} big />
              <Meta k="Podium accuracy" v={pct(model.podium_accuracy ?? 0)} big />
              <Meta k="Features" v={model.features ?? "—"} big />
              <Meta k="Trained on" v={model.trained_on ?? "—"} big />
            </div>
          </section>
        </main>
      )}

      <footer className="foot">
        Endpoint <code>{API_BASE}{ENDPOINTS.prediction}</code> ·{" "}
        {live ? "connected" : "using demo data — start the API to go live"}
      </footer>
    </div>
  );
}

function PodiumStep({ d, place, rank, mounted }) {
  return (
    <div
      className={`step step--${rank} ${mounted ? "is-in" : ""}`}
      style={{ "--team": teamColor(d.team) }}
    >
      <span className="step__rank">{place}</span>
      {/* FIX 4: font-size reduced from clamp(34px,5vw,52px) → clamp(24px,3.5vw,36px) */}
      <span className="step__code">{d.code}</span>
      <span className="step__name">{d.name}</span>
      <span className="step__team">{d.team}</span>
      <span className="step__win">{pct(d.win)} <em>win</em></span>
    </div>
  );
}

function Meta({ k, v, big }) {
  return (
    <div className={`mt ${big ? "mt--big" : ""}`}>
      <span className="mt__k">{k}</span>
      <span className="mt__v">{v}</span>
    </div>
  );
}

/* ============================================================================
   STYLES
   All 4 fixes applied:
   [1] .topbar replaces .bar for header (was colliding with .bar prob-bar)
   [2] .topbar__race gets grid-area:race so header doesn't get truncated
   [3] inactive .tab color lifted from #8A8A96 → #b0b0bc for better contrast
   [4] .step__code font-size reduced so podium names aren't oversized
   ========================================================================== */
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

.f1 *{box-sizing:border-box;margin:0;padding:0}
.f1{
  --bg:#0B0B0F; --bg2:#121218; --surface:#16161D; --line:#23232C;
  --ink:#F2F2F5; --mut:#8A8A96; --red:#E10600;
  min-height:100vh;
  background:
    radial-gradient(1200px 500px at 80% -10%, rgba(225,6,0,.10), transparent 60%),
    radial-gradient(900px 600px at -10% 110%, rgba(54,113,198,.10), transparent 55%),
    var(--bg);
  color:var(--ink);
  font-family:'Inter',system-ui,sans-serif;
  padding:clamp(14px,3vw,32px);
  -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}

/* ── FIX 1 & 2: .topbar (was .bar) ── */
.topbar{
  display:grid;
  grid-template-columns:1fr auto;
  grid-template-rows:auto auto;
  grid-template-areas:
    "wordmark status"
    "race     race";
  column-gap:24px;
  row-gap:10px;
  padding-bottom:18px;
  border-bottom:1px solid var(--line);
}
.wordmark{grid-area:wordmark; display:flex; align-items:center; gap:10px}
.wordmark__tick{width:10px; height:28px; background:var(--red); border-radius:1px;
  box-shadow:0 0 18px rgba(225,6,0,.6)}
.wordmark__text{font-family:'Saira Condensed'; font-weight:800; font-size:26px;
  letter-spacing:.06em; white-space:nowrap}
.wordmark__slash{color:var(--red); margin:0 2px}

/* FIX 2: grid-area:race added here — this was missing, causing header truncation */
.topbar__race{
  grid-area:race;
  display:flex;
  flex-direction:column;
  gap:5px;
}
.topbar__gp{
  font-family:'Saira Condensed'; font-weight:800;
  font-size:clamp(22px,3vw,38px);
  letter-spacing:.06em; line-height:1; text-transform:uppercase;
}
.topbar__circuit{font-size:12px; color:var(--mut); font-family:'JetBrains Mono'; letter-spacing:.04em}

.status{
  grid-area:status; display:flex; align-items:center; gap:8px;
  font-family:'JetBrains Mono'; font-size:11px; letter-spacing:.12em;
  padding:7px 12px; border-radius:999px; border:1px solid var(--line);
  background:var(--surface); white-space:nowrap; align-self:center;
}
.status__dot{width:7px; height:7px; border-radius:50%}
.status--live .status__dot{background:#52E252; box-shadow:0 0 10px #52E252; animation:pulse 1.6s infinite}
.status--mock .status__dot{background:#FFC400}
.status--live{color:#9ff0b0}
.status--mock{color:#ffd86b}
@keyframes pulse{50%{opacity:.35}}

/* ── tabs ── */
.tabs{display:flex; gap:4px; margin:18px 0 24px; flex-wrap:wrap}
.tab{
  font-family:'Saira Condensed'; font-weight:600; font-size:14px; letter-spacing:.04em;
  /* FIX 3: was var(--mut) = #8A8A96, now #b0b0bc for readable contrast */
  color:#b0b0bc;
  background:transparent; border:1px solid transparent; cursor:pointer;
  padding:9px 16px; border-radius:8px; transition:.18s;
}
.tab:hover{color:var(--ink); background:var(--surface)}
.tab--on{color:var(--ink); background:var(--surface); border-color:var(--line); box-shadow:inset 0 -2px 0 var(--red)}

.eyebrow{
  font-family:'JetBrains Mono'; font-size:10.5px; letter-spacing:.22em;
  text-transform:uppercase; color:var(--mut); margin-bottom:14px;
}

/* ── podium ── */
.podium{margin-bottom:26px}
.podium__stage{display:grid; grid-template-columns:1fr 1.15fr 1fr; gap:14px; align-items:end}
.step{
  position:relative;
  background:linear-gradient(180deg,var(--surface),var(--bg2));
  border:1px solid var(--line); border-radius:14px; padding:20px 18px 18px;
  overflow:hidden; opacity:0; transform:translateY(14px);
  transition:.5s cubic-bezier(.2,.7,.2,1); min-width:0;
}
.step.is-in{opacity:1; transform:none}
.step::before{content:""; position:absolute; inset:0 0 auto 0; height:4px; background:var(--team)}
.step::after{
  content:""; position:absolute; left:0; right:0; bottom:0; height:80px;
  background:radial-gradient(120px 70px at 50% 120%, var(--team), transparent 70%);
  opacity:.22; pointer-events:none;
}
.step--gold{padding-top:30px; border-color:#5a4a1e; transition-delay:.05s}
.step--gold::before{height:5px; background:linear-gradient(90deg,#FFD86B,#E8B23A)}
.step--silver{transition-delay:.12s}
.step--bronze{transition-delay:.18s}
.step__rank{
  position:absolute; top:14px; right:16px;
  font-family:'Saira Condensed'; font-weight:800; font-size:46px;
  line-height:.8; color:#fff; opacity:.10;
}
.step--gold .step__rank{opacity:.18; color:#FFD86B; font-size:58px}

/* FIX 4: was clamp(34px,5vw,52px) — too large, PIA/NOR/VER were oversized */
.step__code{
  display:block; font-family:'Saira Condensed'; font-weight:800;
  font-size:clamp(24px,3.5vw,36px);
  letter-spacing:.01em; line-height:.95; color:var(--team);
}
.step__name{display:block; font-weight:600; font-size:14px; margin-top:6px}
.step__team{
  display:block; font-family:'JetBrains Mono'; font-size:10.5px;
  color:var(--mut); letter-spacing:.04em; margin-top:2px;
}
.step__win{
  display:block; margin-top:12px; font-family:'JetBrains Mono';
  font-weight:700; font-size:17px;
}
.step__win em{
  font-style:normal; font-size:10px; color:var(--mut);
  letter-spacing:.1em; text-transform:uppercase; margin-left:4px;
}

/* ── split layout ── */
.split{display:grid; grid-template-columns:1fr 300px; gap:18px; align-items:start}

/* ── timing tower ── */
.tower{
  background:var(--surface); border:1px solid var(--line);
  border-radius:14px; padding:18px 18px 8px;
}
.tower__head{display:flex; justify-content:space-between; align-items:baseline}
.tower__legend{font-family:'JetBrains Mono'; font-size:10px; color:var(--mut); letter-spacing:.1em}
.grid{list-style:none}
.row{
  --team:#8A8A96;
  display:grid; grid-template-columns:6px 30px 46px 1fr 130px;
  align-items:center; gap:12px; padding:9px 4px;
  border-bottom:1px solid var(--line);
  opacity:0; transform:translateX(-8px); animation:rowIn .42s forwards;
}
.row:last-child{border-bottom:0}
.row:hover{background:rgba(255,255,255,.02)}
@keyframes rowIn{to{opacity:1; transform:none}}
.row__bar{
  height:26px; width:4px; border-radius:2px; background:var(--team);
  box-shadow:0 0 10px color-mix(in srgb,var(--team) 60%, transparent);
}
.row__pos{font-family:'JetBrains Mono'; font-size:13px; color:var(--mut); text-align:right}
.row__code{font-family:'Saira Condensed'; font-weight:700; font-size:19px; letter-spacing:.02em}
.row__name{font-size:13.5px; font-weight:500; line-height:1.15; overflow:hidden}
.row__team{
  display:block; font-style:normal; font-family:'JetBrains Mono';
  font-size:10px; color:var(--mut); letter-spacing:.02em;
}
.row__conf{display:flex; align-items:center; gap:8px; justify-content:flex-end}

/* FIX 2: renamed .bar/.bar__fill → .probbar/.probbar__fill — no more header clash */
.probbar{flex:1; height:6px; background:#0d0d12; border-radius:3px; overflow:hidden}
.probbar__fill{
  display:block; height:100%;
  background:linear-gradient(90deg,
    color-mix(in srgb,var(--team) 50%, transparent), var(--team));
  border-radius:3px; transition:width .9s cubic-bezier(.2,.7,.2,1);
}
.row__conf b{
  font-family:'JetBrains Mono'; font-weight:700; font-size:12px;
  min-width:46px; text-align:right;
}

/* ── rail ── */
.rail{display:flex; flex-direction:column; gap:18px}
.card{background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:18px}
.gauge{display:flex; flex-direction:column; gap:2px; margin-bottom:16px}
.gauge__num{
  font-family:'Saira Condensed'; font-weight:800; font-size:46px; line-height:.9;
  background:linear-gradient(90deg,#fff,#9aa0ff);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}
.gauge__lbl{font-family:'JetBrains Mono'; font-size:10px; color:var(--mut); letter-spacing:.08em}
.meta{display:flex; flex-direction:column; gap:10px}
.mt{
  display:flex; justify-content:space-between; align-items:baseline;
  border-top:1px solid var(--line); padding-top:10px;
}
.mt__k{font-size:12px; color:var(--mut)}
.mt__v{font-family:'JetBrains Mono'; font-weight:700; font-size:13px}
.legend{list-style:none; display:flex; flex-direction:column; gap:9px}
.legend li{display:flex; align-items:center; gap:9px; font-size:12px; color:#cfcfd6}
.legend__sw{width:11px; height:11px; border-radius:3px; flex-shrink:0}
.rail__ts{margin-top:14px; font-family:'JetBrains Mono'; font-size:10px; color:var(--mut)}

/* ── standings ── */
.view--standings{display:grid; grid-template-columns:1fr 1fr; gap:18px}
.table{width:100%; border-collapse:collapse}
.table tr{--team:#8A8A96; border-bottom:1px solid var(--line)}
.table tr:last-child{border-bottom:0}
.table__pos{font-family:'JetBrains Mono'; color:var(--mut); width:34px; padding:11px 0; font-size:13px}
.table__bar{width:6px}
.table__bar span{display:block; width:4px; height:24px; border-radius:2px; background:var(--team)}
.table__name{padding:11px 10px; font-weight:600; font-size:14px}
.table__name em{display:block; font-style:normal; font-family:'JetBrains Mono'; font-size:10px; color:var(--mut)}
.table__pts{text-align:right; font-family:'Saira Condensed'; font-weight:700; font-size:20px}

/* ── model ── */
.card--wide{max-width:760px}
.model__name{font-family:'Saira Condensed'; font-weight:700; font-size:30px; margin:4px 0 22px}
.model__grid{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:1px; background:var(--line); border:1px solid var(--line);
  border-radius:12px; overflow:hidden;
}
.mt--big{flex-direction:column; align-items:flex-start; gap:6px; background:var(--surface); border-top:0; padding:18px}
.mt--big .mt__v{font-family:'Saira Condensed'; font-size:24px; font-weight:700}

/* ── footer ── */
.foot{
  margin-top:28px; padding-top:16px; border-top:1px solid var(--line);
  font-family:'JetBrains Mono'; font-size:11px; color:var(--mut);
}
.foot code{color:#b9b9c4}

/* ── responsive ── */
@media (max-width:900px){
  .topbar{grid-template-columns:auto 1fr; row-gap:10px}
  .status{grid-column:1 / -1}
  .split{grid-template-columns:1fr}
  .view--standings{grid-template-columns:1fr}
  .podium__stage{grid-template-columns:1fr}
  .step--gold{order:-1; padding-top:20px}
  .row{grid-template-columns:6px 26px 42px 1fr 96px}
}
@media (prefers-reduced-motion:reduce){
  .row,.step,.probbar__fill,.status__dot{
    animation:none!important; transition:none!important;
    opacity:1!important; transform:none!important;
  }
}
`;