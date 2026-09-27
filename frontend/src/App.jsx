import { useState, useEffect } from 'react'
import { Activity, Database, Server, CheckCircle2, XCircle, RefreshCw, Cpu, ShieldCheck } from 'lucide-react'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:8000/api/v1/health')
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      const data = await res.json()
      setHealth(data)
    } catch (err) {
      console.error('Failed to fetch backend health:', err)
      setError(err.message || 'Failed to connect to backend server')
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg border border-indigo-500/30">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">IncidentIQ</h1>
            <p className="text-xs text-slate-400">AI-Powered DevOps & SRE Incident Response</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-full border border-slate-700">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>System Initialized</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 space-y-8">
        {/* Welcome Hero */}
        <section className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-8 rounded-2xl border border-indigo-900/30 shadow-xl">
          <div className="max-w-2xl space-y-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
              <ShieldCheck className="w-3.5 h-3.5" /> Platform Core Ready
            </span>
            <h2 className="text-3xl font-extrabold text-white tracking-tight">
              Incident Response Assistant
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed">
              IncidentIQ equips SRE and DevOps teams with real-time root cause diagnostics, intelligent triaging, and automated mitigation runbooks.
            </p>
          </div>
        </section>

        {/* Backend & System Status */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Server className="w-5 h-5 text-indigo-400" /> System Health Status
            </h3>
            <button
              onClick={fetchHealth}
              disabled={loading}
              className="flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition text-slate-200 border border-slate-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* API Status */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">FastAPI Backend</span>
                  <div className="text-lg font-bold text-white mt-1">
                    {loading ? 'Checking...' : health?.status === 'healthy' ? 'Operational' : 'Unavailable'}
                  </div>
                </div>
                <div className="p-2 bg-slate-800 rounded-lg text-slate-400">
                  <Cpu className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                <span className="text-slate-400">Status</span>
                {loading ? (
                  <span className="text-slate-400">Checking...</span>
                ) : health?.status === 'healthy' ? (
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-rose-400 font-medium">
                    <XCircle className="w-3.5 h-3.5" /> Down
                  </span>
                )}
              </div>
            </div>

            {/* Database Status */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">SQLite Storage</span>
                  <div className="text-lg font-bold text-white mt-1">
                    {loading ? 'Checking...' : health?.database === 'connected' ? 'Connected' : 'Disconnected'}
                  </div>
                </div>
                <div className="p-2 bg-slate-800 rounded-lg text-slate-400">
                  <Database className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                <span className="text-slate-400">Database</span>
                {loading ? (
                  <span className="text-slate-400">Checking...</span>
                ) : health?.database === 'connected' ? (
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Connected
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-rose-400 font-medium">
                    <XCircle className="w-3.5 h-3.5" /> Error
                  </span>
                )}
              </div>
            </div>

            {/* Service Version */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Core Version</span>
                  <div className="text-lg font-bold text-white mt-1">
                    {health?.version ? `v${health.version}` : 'v0.1.0'}
                  </div>
                </div>
                <div className="p-2 bg-slate-800 rounded-lg text-slate-400">
                  <Activity className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                <span className="text-slate-400">Environment</span>
                <span className="text-indigo-400 font-medium">Development</span>
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-rose-950/40 border border-rose-800/50 rounded-xl p-4 text-xs text-rose-300 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>Backend Connection Error: {error}. Ensure FastAPI backend server is running on port 8000.</span>
              </div>
              <button
                onClick={fetchHealth}
                className="underline hover:text-rose-200 shrink-0 ml-2"
              >
                Retry
              </button>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 px-6 py-4 text-center text-xs text-slate-500">
        IncidentIQ &copy; {new Date().getFullYear()} — DevOps & SRE Incident Management Platform
      </footer>
    </div>
  )
}

export default App
