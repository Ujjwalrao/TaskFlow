import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Topbar from '../components/Topbar.jsx'
import { semanticSearch } from '../lib/api.js'
import { Search as SearchIcon, Sparkles } from 'lucide-react'

const typeColors = {
  task: 'bg-blue-50 text-blue-600 dark:bg-blue-500/10',
  habit: 'bg-orange-50 text-orange-600 dark:bg-orange-500/10',
  goal: 'bg-purple-50 text-purple-600 dark:bg-purple-500/10',
  document: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10',
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    try {
      const data = await semanticSearch(query)
      setResults(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Topbar title="Search" breadcrumb="Workspace" />
      <div className="p-8 max-w-2xl space-y-6">
        <div className="glass-card rounded-xl2 p-4 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <Sparkles size={16} className="text-brand-500" />
          Semantic search — powered by a local embedding model, no API calls, runs fully offline.
        </div>
        <form onSubmit={submit} className="flex gap-3">
          <div className="relative flex-1">
            <SearchIcon size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              className="input-premium w-full pl-11"
              placeholder="Search anything, e.g. 'things about the client presentation'"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button className="btn-primary text-sm">Search</button>
        </form>

        {loading && <p className="text-sm text-gray-400">Searching...</p>}
        {!loading && searched && results.length === 0 && <p className="text-sm text-gray-400">No relevant matches found.</p>}

        <div className="space-y-2">
          <AnimatePresence>
            {results.map((r, i) => (
              <motion.div
                key={`${r.type}-${r.id}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="premium-card p-4 flex items-center justify-between"
              >
                <div>
                  <span className={`badge capitalize ${typeColors[r.type] || ''}`}>{r.type}</span>
                  <p className="text-sm text-gray-800 dark:text-gray-200 mt-2">{r.title}</p>
                </div>
                <span className="text-xs font-semibold text-brand-500">{Math.round(r.score * 100)}% match</span>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
