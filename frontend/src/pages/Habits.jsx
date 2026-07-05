import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Topbar from '../components/Topbar.jsx'
import { getHabits, createHabit, logHabit, deleteHabit } from '../lib/api.js'
import { Flame, Trash2, Check, Plus } from 'lucide-react'

export default function Habits() {
  const [habits, setHabits] = useState([])
  const [title, setTitle] = useState('')
  const [frequency, setFrequency] = useState('daily')
  const [showForm, setShowForm] = useState(false)

  const load = () => getHabits().then(setHabits).catch(() => {})
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    await createHabit({ title, frequency })
    setTitle('')
    setShowForm(false)
    load()
  }

  const markDoneToday = async (id) => {
    await logHabit(id)
    load()
  }

  const remove = async (id) => {
    await deleteHabit(id)
    load()
  }

  const today = new Date().toISOString().slice(0, 10)

  return (
    <div>
      <Topbar title="Habits" breadcrumb="Workspace" />
      <div className="p-8 space-y-6 max-w-4xl">
        <div className="flex justify-end">
          <button onClick={() => setShowForm((s) => !s)} className="btn-primary flex items-center gap-2 text-sm">
            <Plus size={16} /> New Habit
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
                placeholder="New habit, e.g. Read 20 minutes"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                autoFocus
              />
              <select className="input-premium" value={frequency} onChange={(e) => setFrequency(e.target.value)}>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
              <button className="btn-primary text-sm">Add</button>
            </motion.form>
          )}
        </AnimatePresence>

        <div className="grid gap-5 sm:grid-cols-2">
          {habits.length === 0 && <p className="text-sm text-gray-400">No habits yet — add one above.</p>}
          {habits.map((h, i) => {
            const doneToday = (h.logged_dates || []).includes(today)
            return (
              <motion.div
                key={h.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="premium-card p-5"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-gray-100">{h.title}</p>
                    <p className="text-xs text-gray-400 capitalize">{h.frequency}</p>
                  </div>
                  <button onClick={() => remove(h.id)} className="text-gray-300 hover:text-red-500 transition-colors">
                    <Trash2 size={16} />
                  </button>
                </div>

                <div className="flex items-center gap-2 mt-4">
                  <motion.div whileHover={{ scale: 1.1 }}>
                    <Flame size={20} className="text-orange-500" />
                  </motion.div>
                  <span className="text-sm font-bold text-gray-800 dark:text-gray-200">
                    {h.current_streak} day streak
                  </span>
                  <span className="text-xs text-gray-400 badge bg-gray-100 dark:bg-gray-800">best: {h.longest_streak}</span>
                </div>

                <button
                  onClick={() => markDoneToday(h.id)}
                  disabled={doneToday}
                  className={`mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                    doneToday
                      ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 cursor-default'
                      : 'btn-primary'
                  }`}
                >
                  <Check size={16} />
                  {doneToday ? 'Done for today' : 'Mark done today'}
                </button>
              </motion.div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
