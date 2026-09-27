import React, { useState, useEffect } from 'react';
import {
  Brain,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Clock,
  ShieldAlert,
  ArrowRight,
  Send,
  FileText
} from 'lucide-react';
import { fetchIncidentById, analyzeIncident, resolveIncident } from '../api';

export default function IncidentInvestigation({ incidentId, incidents, onSelectIncident }) {
  const [selectedId, setSelectedId] = useState(incidentId || (incidents.length > 0 ? incidents[0].id : ''));
  const [incident, setIncident] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Resolution modal state
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [rootCauseInput, setRootCauseInput] = useState('');
  const [resolutionInput, setResolutionInput] = useState('');
  const [resolving, setResolving] = useState(false);

  useEffect(() => {
    if (incidentId) setSelectedId(incidentId);
  }, [incidentId]);

  useEffect(() => {
    if (selectedId) {
      loadAndAnalyze(selectedId);
    }
  }, [selectedId]);

  const loadAndAnalyze = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const inc = await fetchIncidentById(id);
      setIncident(inc);

      const inv = await analyzeIncident(id);
      setInvestigation(inv);
    } catch (err) {
      console.error('Investigation error:', err);
      setError(err.message || 'Failed to analyze incident');
    } finally {
      setLoading(false);
    }
  };

  const handleResolveSubmit = async (e) => {
    e.preventDefault();
    if (!resolutionInput.trim()) return;

    setResolving(true);
    try {
      const updated = await resolveIncident(selectedId, {
        root_cause: rootCauseInput.trim() || undefined,
        resolution: resolutionInput.trim(),
        outcome: 'Resolved',
      });
      setIncident(updated);
      setShowResolveModal(false);
      setRootCauseInput('');
      setResolutionInput('');
      // Re-run analysis after resolution
      loadAndAnalyze(selectedId);
    } catch (err) {
      alert(`Resolution failed: ${err.message}`);
    } finally {
      setResolving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Selector Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider shrink-0">Select Incident:</span>
          <select
            value={selectedId}
            onChange={(e) => {
              setSelectedId(e.target.value);
              if (onSelectIncident) onSelectIncident(e.target.value);
            }}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500 w-full md:w-72"
          >
            {incidents.map((inc) => (
              <option key={inc.id} value={inc.id}>
                {inc.id} - {inc.service} ({inc.outcome})
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3">
          {incident && incident.outcome.toLowerCase() !== 'resolved' && (
            <button
              onClick={() => setShowResolveModal(true)}
              className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" /> Resolve & Retain in Hindsight
            </button>
          )}
          <button
            onClick={() => loadAndAnalyze(selectedId)}
            disabled={loading}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-700 transition flex items-center gap-1.5 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Re-analyze
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center space-y-3 bg-slate-900 border border-slate-800 rounded-xl">
          <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
          <p className="text-sm text-slate-300 font-semibold">Running IncidentIQ AI Workflow...</p>
          <p className="text-xs text-slate-500">Retrieving Hindsight memories & querying Groq LLM</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/40 border border-rose-800/50 rounded-xl text-xs text-rose-300">
          <ShieldAlert className="w-5 h-5 text-rose-400 mb-2" />
          <span className="font-semibold">Investigation Error:</span> {error}
        </div>
      ) : investigation && incident ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Investigation Panel (2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Incident Header Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950 px-2.5 py-1 rounded border border-indigo-800/50">
                    {incident.id}
                  </span>
                  <h2 className="text-lg font-bold text-white">{incident.service}</h2>
                  <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                    incident.severity === 'critical' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                    incident.severity === 'high' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                    'bg-slate-800 text-slate-300 border border-slate-700'
                  }`}>
                    {incident.severity}
                  </span>
                </div>

                <span className={`text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1 ${
                  incident.outcome.toLowerCase() === 'resolved'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                }`}>
                  {incident.outcome}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
                <div>
                  <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block mb-1">Primary Error</span>
                  <p className="font-mono bg-slate-950 p-2.5 rounded border border-slate-800 text-slate-200">{incident.error}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block mb-1">Symptoms</span>
                  <p className="bg-slate-950 p-2.5 rounded border border-slate-800 text-slate-300">{incident.symptoms}</p>
                </div>
              </div>

              {incident.root_cause && (
                <div className="text-xs bg-emerald-950/30 border border-emerald-800/50 rounded-lg p-3 text-emerald-300 space-y-1">
                  <span className="font-bold block uppercase text-[10px] tracking-wider text-emerald-400">Resolved Root Cause</span>
                  <p>{incident.root_cause}</p>
                </div>
              )}
            </div>

            {/* Groq AI Root Cause Analysis & Recommended Action */}
            <div className="bg-gradient-to-br from-slate-900 via-indigo-950/30 to-slate-900 border border-indigo-900/40 rounded-xl p-6 shadow-md space-y-5">
              <div className="flex items-center justify-between border-b border-indigo-900/40 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-indigo-400" /> Groq AI Diagnosis & Recommendation
                </h3>
                <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                  investigation.ai_analysis?.confidence === 'high' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                  investigation.ai_analysis?.confidence === 'medium' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  'bg-slate-800 text-slate-300 border border-slate-700'
                }`}>
                  Confidence: {investigation.ai_analysis?.confidence || 'medium'}
                </span>
              </div>

              {/* Recommended Action Box */}
              <div className="bg-indigo-900/20 border border-indigo-500/30 rounded-lg p-4 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-300 block">Recommended Remediation Action</span>
                <p className="text-sm font-semibold text-white leading-relaxed">{investigation.recommended_action}</p>
              </div>

              {/* Probable Root Cause */}
              <div className="space-y-1.5 text-xs">
                <span className="font-semibold text-slate-400 uppercase tracking-wider text-[10px] block">Probable Root Cause</span>
                <p className="text-slate-200 bg-slate-950 p-3 rounded-lg border border-slate-800 leading-relaxed">
                  {investigation.ai_analysis?.probable_root_cause}
                </p>
              </div>

              {/* Reasoning & Explanation */}
              <div className="space-y-1.5 text-xs">
                <span className="font-semibold text-slate-400 uppercase tracking-wider text-[10px] block">AI Reasoning & Evidence Explanation</span>
                <p className="text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800 leading-relaxed">
                  {investigation.explanation}
                </p>
              </div>
            </div>
          </div>

          {/* Hindsight Memories Sidebar (1 col) */}
          <div className="space-y-6">
            {/* Recalled Memories Summary */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Brain className="w-4 h-4 text-purple-400" /> Hindsight Recalled Memories
                </h3>
                <span className="text-[10px] text-purple-300 bg-purple-950 px-2 py-0.5 rounded border border-purple-800">
                  {investigation.similar_historical_incidents?.length || 0} Matches
                </span>
              </div>

              {/* Previous Root Causes */}
              {investigation.previous_root_causes?.length > 0 && (
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Previous Known Root Causes</span>
                  <div className="space-y-1.5">
                    {investigation.previous_root_causes.map((rc, idx) => (
                      <div key={idx} className="bg-slate-950 p-2.5 rounded border border-slate-800 text-xs text-purple-200">
                        • {rc}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Previous Resolutions */}
              {investigation.previous_resolutions?.length > 0 && (
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Previous Known Resolutions</span>
                  <div className="space-y-1.5">
                    {investigation.previous_resolutions.map((res, idx) => (
                      <div key={idx} className="bg-slate-950 p-2.5 rounded border border-slate-800 text-xs text-emerald-200">
                        ✓ {res}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {investigation.similar_historical_incidents?.length === 0 && (
                <div className="py-6 text-center text-xs text-slate-500">
                  No matching historical memories found in Hindsight for this incident query.
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}

      {/* Resolve Incident Modal */}
      {showResolveModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Resolve Incident & Retain in Hindsight
            </h3>

            <p className="text-xs text-slate-400">
              Documenting the root cause and resolution will retain this experience into Hindsight persistent memory for future incidents to recall.
            </p>

            <form onSubmit={handleResolveSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Identified Root Cause</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Connection pool exhaustion due to session leak during traffic surge"
                  value={rootCauseInput}
                  onChange={(e) => setRootCauseInput(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">
                  Resolution Steps Taken <span className="text-rose-400">*</span>
                </label>
                <textarea
                  rows={3}
                  placeholder="e.g. Increased connection pool size from 20 to 100 and deployed hotfix for session leak"
                  value={resolutionInput}
                  onChange={(e) => setResolutionInput(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowResolveModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={resolving}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition disabled:opacity-50"
                >
                  {resolving ? 'Resolving...' : 'Confirm & Retain Memory'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
