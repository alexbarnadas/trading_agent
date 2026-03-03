import React, { useState, useEffect } from 'react'
import { Activity, Briefcase, Newspaper, ShieldAlert, Wifi, Search, Settings, ChevronRight, BarChart2, TrendingUp, TrendingDown, ExternalLink, Clock, Gauge, Users, Brain } from 'lucide-react'

function App() {
  const [status, setStatus] = useState({ equity: 100000, market_status: 'closed' })
  const [candidates, setCandidates] = useState({})
  const [selectedCandidate, setSelectedCandidate] = useState(null)
  const [showSettings, setShowSettings] = useState(false)
  const [settings, setSettings] = useState({ risk_aggression: 1.0, watchlist: [], autonomous_mode: false })
  const [positions, setPositions] = useState([])
  const [news, setNews] = useState([])
  const [sentiment, setSentiment] = useState({ fear_greed_value: 50, fear_greed_label: 'Neutral' })

  // Fetch status, candidates, positions periodically (5s)
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statResp, candResp, settResp, posResp] = await Promise.all([
          fetch('http://localhost:8000/status').then(r => r.json()),
          fetch('http://localhost:8000/candidates').then(r => r.json()),
          fetch('http://localhost:8000/settings').then(r => r.json()),
          fetch('http://localhost:8000/positions').then(r => r.json())
        ])
        setStatus(statResp)
        setCandidates(candResp)
        setSettings(settResp)
        setPositions(posResp || [])
      } catch (e) { console.error("Poll error", e) }
    }
    fetchData()
    const timer = setInterval(fetchData, 5000)
    return () => clearInterval(timer)
  }, [])

  // Fetch news + sentiment less frequently (60s)
  useEffect(() => {
    const fetchNewsAndSentiment = async () => {
      try {
        const [newsResp, sentResp] = await Promise.all([
          fetch('http://localhost:8000/news').then(r => r.json()),
          fetch('http://localhost:8000/market-sentiment').then(r => r.json())
        ])
        setNews(Array.isArray(newsResp) ? newsResp : [])
        setSentiment(sentResp)
      } catch (e) { console.error("News poll error", e) }
    }
    fetchNewsAndSentiment()
    const timer = setInterval(fetchNewsAndSentiment, 60000)
    return () => clearInterval(timer)
  }, [])

  const saveSettings = async (newSettings) => {
    await fetch('http://localhost:8000/settings', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSettings)
    })
    setSettings(newSettings)
  }

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return ''
    try {
      const ts = typeof timestamp === 'number' ? timestamp * 1000 : new Date(timestamp).getTime()
      const diff = Date.now() - ts
      const mins = Math.floor(diff / 60000)
      if (mins < 1) return 'Just now'
      if (mins < 60) return `${mins}m ago`
      const hrs = Math.floor(mins / 60)
      if (hrs < 24) return `${hrs}h ago`
      return `${Math.floor(hrs / 24)}d ago`
    } catch { return '' }
  }

  const getFearGreedColor = (val) => {
    if (val <= 25) return '#f85149'
    if (val <= 45) return '#f0883e'
    if (val <= 55) return '#8b949e'
    if (val <= 75) return '#58a6ff'
    return '#3fb950'
  }

  const getRsiColor = (val) => {
    const v = parseFloat(val)
    if (isNaN(v)) return '#8b949e'
    if (v > 70) return '#f85149'
    if (v < 30) return '#3fb950'
    return '#58a6ff'
  }

  return (
    <div className="dashboard-layout">
      {/* ========== LEFT SIDEBAR ========== */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <Newspaper size={18} />
          <h2>Market Feed</h2>
        </div>

        {/* Fear & Greed Gauge */}
        <div className="sentiment-gauge">
          <div className="gauge-header">
            <Gauge size={14} />
            <span>Fear & Greed Index</span>
          </div>
          <div className="gauge-bar-container">
            <div className="gauge-bar" style={{
              width: `${sentiment.fear_greed_value}%`,
              background: `linear-gradient(90deg, #f85149, #f0883e, #58a6ff, #3fb950)`
            }} />
            <div className="gauge-needle" style={{ left: `${sentiment.fear_greed_value}%` }} />
          </div>
          <div className="gauge-value" style={{ color: getFearGreedColor(sentiment.fear_greed_value) }}>
            {sentiment.fear_greed_value} — {sentiment.fear_greed_label}
          </div>
        </div>

        {/* News Feed */}
        <div className="news-feed">
          {news.length === 0 ? (
            <div className="news-empty">
              <Clock size={20} />
              <p>Waiting for news from watchlist...</p>
            </div>
          ) : (
            news.map((item, i) => (
              <a key={i} className="news-item" href={item.url} target="_blank" rel="noopener noreferrer">
                <div className="news-item-header">
                  <span className="news-symbol-badge">{item.symbol}</span>
                  <span className="news-time">{formatTimeAgo(item.timestamp)}</span>
                </div>
                <h4 className="news-headline">{item.headline || 'Untitled'}</h4>
                {item.summary && <p className="news-summary">{item.summary}</p>}
                <div className="news-source">
                  <ExternalLink size={11} />
                  <span>{item.source}</span>
                </div>
              </a>
            ))
          )}
        </div>
      </aside>

      {/* ========== MAIN CONTENT ========== */}
      <main className="main-content">
        <header className="header">
          <div>
            <h1>ANTIGRAVITY MANAGEMENT HUB</h1>
            <div className="status-indicator">
              <div className="dot online"></div>
              <span>Auto-Pilot: {settings.autonomous_mode ? 'ON' : 'OFF'} (Waiting for News)</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button onClick={() => setShowSettings(true)} className="btn-icon"><Settings size={20} /></button>
            <div className="status-indicator">
              <Wifi size={16} />
              <span>Alpaca Paper: ACTIVE</span>
            </div>
          </div>
        </header>

        {/* SYSTEM METRICS */}
        <div className="grid metrics-grid">
          <div className="card metric-card">
            <div className="stat-label">Total Equity</div>
            <div className="stat-value">${parseFloat(status.equity || 0).toLocaleString()}</div>
            <div className="badge badge-profit">+1.2% Daily</div>
          </div>
          <div className="card metric-card">
            <div className="stat-label">Active Candidates</div>
            <div className="stat-value">{Object.keys(candidates).length}</div>
            <div className="stat-label">Evaluating Watchlist...</div>
          </div>
          <div className="card metric-card">
            <div className="stat-label">Market Status</div>
            <div className="stat-value" style={{ textTransform: 'capitalize' }}>{status.market_status}</div>
          </div>
          <div className="card metric-card">
            <div className="stat-label">Buying Power</div>
            <div className="stat-value">${parseFloat(status.buying_power || 0).toLocaleString()}</div>
          </div>
        </div>

        <div className="grid" style={{ marginTop: '1.5rem', gridTemplateColumns: '2fr 1fr' }}>
          {/* DISCOVERY HUB */}
          <div className="card">
            <div className="stat-label" style={{ marginBottom: '1rem' }}><Search size={16} /> Candidate Evaluation Hub</div>
            <div className="candidate-grid">
              {Object.entries(candidates).map(([symbol, data]) => (
                <div key={symbol} className={`candidate-card ${selectedCandidate === symbol ? 'active' : ''}`} onClick={() => setSelectedCandidate(symbol)}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="ticker-label">{symbol}</span>
                    <span className={`badge badge-${data.status === 'approved' ? 'profit' : 'risk'}`}>{data.status}</span>
                  </div>
                  <div className="cand-reason">{data.reason}</div>

                  {/* Expanded indicator row */}
                  <div className="cand-indicators">
                    <div className="cand-ind-item">
                      <BarChart2 size={12} />
                      <span>Sent: {data.sentiment || '...'}</span>
                    </div>
                    {data.indicators?.RSI && (
                      <div className="cand-ind-item">
                        <span className="mini-dot" style={{ background: getRsiColor(data.indicators.RSI) }}></span>
                        <span>RSI: {parseFloat(data.indicators.RSI).toFixed(1)}</span>
                      </div>
                    )}
                    {data.indicators?.price_change_pct !== undefined && (
                      <div className="cand-ind-item">
                        {data.indicators.price_change_pct >= 0 ? <TrendingUp size={12} style={{ color: '#3fb950' }} /> : <TrendingDown size={12} style={{ color: '#f85149' }} />}
                        <span style={{ color: data.indicators.price_change_pct >= 0 ? '#3fb950' : '#f85149' }}>
                          {data.indicators.price_change_pct >= 0 ? '+' : ''}{parseFloat(data.indicators.price_change_pct).toFixed(2)}%
                        </span>
                      </div>
                    )}
                    {data.indicators?.SMA_20 && (
                      <div className="cand-ind-item">
                        <span>SMA: {parseFloat(data.indicators.SMA_20).toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {Object.keys(candidates).length === 0 && (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#8b949e' }}>
                  No active signals. Bot is monitoring watchlist for breaking news...
                </div>
              )}
            </div>
          </div>

          {/* INSIGHTS PANEL */}
          <div className="card">
            <div className="stat-label"><Activity size={16} /> Candidate Deep-Dive</div>
            {selectedCandidate ? (
              <div className="insight-view">
                <h2>{selectedCandidate}</h2>
                <div className="insight-score">
                  <span className="stat-label">AI Signal Confidence</span>
                  <div className="stat-value">{(candidates[selectedCandidate].confidence * 100 || 0).toFixed(0)}%</div>
                </div>
                <div className="insight-box">
                  <h4>Agent Rationale</h4>
                  <p>{candidates[selectedCandidate].insights || "Analyzing technical indicators and news impact..."}</p>
                </div>

                {/* EXPANDED INDICATORS GRID */}
                <div style={{ marginTop: '1rem' }}>
                  <h4>Technical Indicators</h4>
                  <div className="indicators-grid">
                    <div className="indicator-pill">
                      <span className="ind-label">RSI</span>
                      <span className="ind-value" style={{ color: getRsiColor(candidates[selectedCandidate].indicators?.RSI) }}>
                        {candidates[selectedCandidate].indicators?.RSI ? parseFloat(candidates[selectedCandidate].indicators.RSI).toFixed(1) : '...'}
                      </span>
                      {candidates[selectedCandidate].indicators?.RSI && (
                        <div className="mini-bar-container">
                          <div className="mini-bar" style={{
                            width: `${Math.min(100, parseFloat(candidates[selectedCandidate].indicators.RSI))}%`,
                            background: getRsiColor(candidates[selectedCandidate].indicators.RSI)
                          }} />
                        </div>
                      )}
                    </div>
                    <div className="indicator-pill">
                      <span className="ind-label">MACD</span>
                      <span className="ind-value">{candidates[selectedCandidate].indicators?.MACD || '...'}</span>
                    </div>
                    <div className="indicator-pill">
                      <span className="ind-label">SMA 20</span>
                      <span className="ind-value">{candidates[selectedCandidate].indicators?.SMA_20 ? parseFloat(candidates[selectedCandidate].indicators.SMA_20).toFixed(2) : '...'}</span>
                    </div>
                    <div className="indicator-pill">
                      <span className="ind-label">Volume</span>
                      <span className="ind-value">{candidates[selectedCandidate].indicators?.volume ? parseInt(candidates[selectedCandidate].indicators.volume).toLocaleString() : '...'}</span>
                    </div>
                  </div>
                </div>

                {/* SMART MONEY / ANALYST */}
                <div style={{ marginTop: '1rem' }}>
                  <h4>Intelligence Signals</h4>
                  <div className="indicators-grid">
                    <div className="indicator-pill signal-pill">
                      <div className="signal-icon"><Users size={14} /></div>
                      <div>
                        <span className="ind-label">Analyst</span>
                        <span className="ind-value">{candidates[selectedCandidate].indicators?.analyst_consensus || '...'}</span>
                      </div>
                    </div>
                    <div className="indicator-pill signal-pill">
                      <div className="signal-icon"><Brain size={14} /></div>
                      <div>
                        <span className="ind-label">Smart $</span>
                        <span className="ind-value">
                          {candidates[selectedCandidate].indicators?.smart_money_bias !== undefined
                            ? `${candidates[selectedCandidate].indicators.smart_money_bias >= 0 ? '+' : ''}${parseFloat(candidates[selectedCandidate].indicators.smart_money_bias).toFixed(3)}`
                            : '...'}
                        </span>
                      </div>
                    </div>
                    <div className="indicator-pill signal-pill">
                      <div className="signal-icon"><Gauge size={14} /></div>
                      <div>
                        <span className="ind-label">Fear/Greed</span>
                        <span className="ind-value" style={{ color: getFearGreedColor(sentiment.fear_greed_value) }}>
                          {sentiment.fear_greed_value}
                        </span>
                      </div>
                    </div>
                    {candidates[selectedCandidate].indicators?.price_change_pct !== undefined && (
                      <div className="indicator-pill signal-pill">
                        <div className="signal-icon">
                          {candidates[selectedCandidate].indicators.price_change_pct >= 0
                            ? <TrendingUp size={14} style={{ color: '#3fb950' }} />
                            : <TrendingDown size={14} style={{ color: '#f85149' }} />}
                        </div>
                        <div>
                          <span className="ind-label">Δ Price</span>
                          <span className="ind-value" style={{ color: candidates[selectedCandidate].indicators.price_change_pct >= 0 ? '#3fb950' : '#f85149' }}>
                            {candidates[selectedCandidate].indicators.price_change_pct >= 0 ? '+' : ''}
                            {parseFloat(candidates[selectedCandidate].indicators.price_change_pct).toFixed(2)}%
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#8b949e' }}>
                Select a candidate to view deep-dive analytics and AI reasoning.
              </div>
            )}
          </div>
        </div>

        {/* POSITIONS TABLE */}
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <div className="stat-label"><Briefcase size={16} /> Active Management Positions</div>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#8b949e', fontSize: '0.8rem' }}>
                <th style={{ padding: '0.5rem' }}>ASSET</th>
                <th>QTY</th>
                <th>VALUE</th>
                <th>UNREALIZED PL</th>
              </tr>
            </thead>
            <tbody>
              {positions.map(p => (
                <tr key={p.symbol}>
                  <td style={{ padding: '0.5rem' }}>{p.symbol}</td>
                  <td>{p.qty}</td>
                  <td>${parseFloat(p.market_value).toLocaleString()}</td>
                  <td style={{ color: parseFloat(p.unrealized_pl) >= 0 ? '#3fb950' : '#f85149' }}>
                    {parseFloat(p.unrealized_pl) >= 0 ? '+' : ''}${parseFloat(p.unrealized_pl).toLocaleString()}
                  </td>
                </tr>
              ))}
              {positions.length === 0 && (
                <tr><td colSpan="4" style={{ textAlign: 'center', padding: '1rem', color: '#8b949e' }}>No open positions.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </main>

      {/* SETTINGS MODAL */}
      {showSettings && (
        <div className="modal-overlay">
          <div className="modal-content card">
            <h2>System Management Settings</h2>
            <div className="setting-group">
              <label>Risk Aggression Multiplier: {settings.risk_aggression}x</label>
              <input type="range" min="0.5" max="2.0" step="0.1" value={settings.risk_aggression}
                onChange={(e) => setSettings({ ...settings, risk_aggression: parseFloat(e.target.value) })} />
            </div>
            <div className="setting-group">
              <label>Watchlist (Comma separated)</label>
              <input type="text" value={settings.watchlist.join(', ')}
                onChange={(e) => setSettings({ ...settings, watchlist: e.target.value.split(',').map(s => s.trim()) })} />
            </div>
            <div className="setting-group" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <input type="checkbox" checked={settings.autonomous_mode}
                onChange={(e) => setSettings({ ...settings, autonomous_mode: e.target.checked })} />
              <label>Enable Autonomous Execution (Auto-Pilot)</label>
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
              <button className="btn-primary" onClick={() => { saveSettings(settings); setShowSettings(false); }}>Apply Changes</button>
              <button className="btn-secondary" onClick={() => setShowSettings(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
