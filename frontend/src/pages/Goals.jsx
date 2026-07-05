import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Topbar from '../components/Topbar.jsx'
import { getGoals, createGoal, deleteGoal } from '../lib/api.js'
import { Trash2, Plus, Target } from 'lucide-react'

export default function Goals() {
  const [goals, setGoals] = useState([])
  const [title, setTitle] = useState('')
  const [targetDate, setTargetDate] = useState('')
  const [showForm, setShowForm] = useState(false)

  const load = () => getGoals().then(setGoals).catch(() => {})
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    await createGoal({ title, target_date: targetDate || null })
    setTitle('')
    setTargetDate('')
    setShowForm(false)
    load()
  }

  const remove = async (id) => {
    await deleteGoal(id)
    load()
  }

  return (
    <div>
      <Topbar title="Goals" breadcrumb="Workspace" />
      <div className="p-8 space-y-6 max-w-4xl">
        <div className="flex justify-end">
          <button onClick={() => setShowForm((s) => !s)} className="btn-primary flex items-center gap-2 text-sm">
            <Plus size={16} /> New Goal
          </button>
        </div>

        <AnimatePresence>
          {showForm && (
            <motion.form
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              onSubmit={submit}
              className="premium-card p-5 flex gap-3 overflow-hidden"
            >
              <input
                className="input-premium flex-1"
                placeholder="New goal, e.g. Ship portfolio v2"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                autoFocus
              />
              <input type="date" className="input-premium" value={targetDate} onChange={(e) => setTargetDate(e.target.value)} />
              <button className="btn-primary text-sm">Add</button>
            </motion.form>
          )}
        </AnimatePresence>

        <div className="space-y-4">
          {goals.length === 0 && <p className="text-sm text-gray-400">No goals yet — add one above.</p>}
          {goals.map((g, i) => (
            <motion.div
              key={g.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="premium-card p-5"
            >
              <div className="flex justify-between items-start gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <div className="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center shrink-0 mt-0.5">
                    <Target size={16} className="text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900 dark:text-gray-100">{g.title}</p>
                    {g.target_date && <p className="text-xs text-gray-400 mt-0.5">Target: {g.target_date}</p>}
                    <div className="mt-3">
                      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${g.progress}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className="h-full bg-brand-gradient rounded-full"
                        />
                      </div>
                      <p className="text-xs text-gray-400 mt-1.5">{g.progress}% · {g.task_count} linked tasks</p>
                    </div>
                  </div>
                </div>
                <button onClick={() => remove(g.id)} className="text-gray-300 hover:text-red-500 transition-colors">
                  <Trash2 size={16} />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
