import React, { useState } from 'react';
import { Brain, Search, Sparkles, RefreshCw, Layers } from 'lucide-react';
import { recallMemories, reflectMemories } from '../api';

export default function MemoryExplorer() {
  const [activeTab, setActiveTab] = useState('recall');

  // Recall states
  const [recallQuery, setRecallQuery] = useState('Database connection pool timeout payment');
  const [recallResults, setRecallResults] = useState(null);
  const [recalling, setRecalling] = useState(false);

  // Reflect states
  const [reflectQuery, setReflectQuery] = useState('What are the recurring root causes across database and network outages?');
  const [reflectResults, setReflectResults] = useState(null);
  const [reflecting, setReflecting] = useState(false);

  const handleRecall = async (e) => {
    if (e) e.preventDefault();
    setRecalling(true);
    try {
      const res = await recallMemories({ query: recallQuery });
      setRecallResults(res);
    } catch (err) {
      alert(`Recall failed: ${err.message}`);
    } finally {
      setRecalling(false);
    }
  };

  const handleReflect = async (e) => {
    if (e) e.preventDefault();
    setReflecting(true);
    try {
      const res = await reflectMemories({ query: reflectQuery });
      setReflectResults(res);
    } catch (err) {
      alert(`Reflect failed: ${err.message}`);
    } finally {
      setReflecting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Brain className="w-6 h-6 text-purple-400" /> Hindsight Memory Operations
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Direct interface to query RECALL memory index and synthesize REFLECT cross-incident takeaways.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('recall')}
            className={`px-4 py-1.5 rounded-md transition flex items-center gap-1.5 ${
              activeTab === 'recall' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-3.5 h-3.5" /> RECALL Memories
          </button>
          <button
            onClick={() => setActiveTab('reflect')}
            className={`px-4 py-1.5 rounded-md transition flex items-center gap-1.5 ${
              activeTab === 'reflect' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" /> REFLECT Patterns
          </button>
        </div>
      </div>

      {/* RECALL TAB */}
      {activeTab === 'recall' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
          <form onSubmit={handleRecall} className="space-y-3">
            <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
              Search Historical Memory Index
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={recallQuery}
                onChange={(e) => setRecallQuery(e.target.value)}
                placeholder="Enter query, service name, or error details..."
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-purple-500 font-mono"
              />
              <button
                type="submit"
                disabled={recalling}
                className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition flex items-center gap-1.5 disabled:opacity-50 shrink-0"
              >
                <Search className="w-3.5 h-3.5" /> {recalling ? 'Searching...' : 'RECALL'}
              </button>
            </div>
          </form>

          {recallResults && (
            <div className="space-y-3 pt-4 border-t border-slate-800">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Recalled Results (Bank: {recallResults.bank_id})
              </span>
              <pre className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs text-purple-300 font-mono overflow-x-auto whitespace-pre-wrap max-h-96">
                {JSON.stringify(recallResults.results, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* REFLECT TAB */}
      {activeTab === 'reflect' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
          <form onSubmit={handleReflect} className="space-y-3">
            <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
              Synthesize Patterns Across Historical Incidents
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={reflectQuery}
                onChange={(e) => setReflectQuery(e.target.value)}
                placeholder="Ask high-level architectural or pattern synthesis question..."
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-purple-500"
              />
              <button
                type="submit"
                disabled={reflecting}
                className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition flex items-center gap-1.5 disabled:opacity-50 shrink-0"
              >
                <Sparkles className="w-3.5 h-3.5" /> {reflecting ? 'Synthesizing...' : 'REFLECT'}
              </button>
            </div>
          </form>

          {reflectResults && (
            <div className="space-y-3 pt-4 border-t border-slate-800">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Reflected Pattern Output (Bank: {reflectResults.bank_id})
              </span>
              <pre className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs text-purple-300 font-mono overflow-x-auto whitespace-pre-wrap max-h-96">
                {JSON.stringify(reflectResults.results, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
