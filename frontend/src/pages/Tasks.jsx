import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Topbar from '../components/Topbar.jsx'
import { getTasks, createTask, updateTask, deleteTask, getMembers } from '../lib/api.js'
import { Trash2, Repeat, Plus, Circle, Clock3, CheckCircle2 } from 'lucide-react'

const RECURRENCE_OPTIONS = [
  { value: '', label: 'No repeat' },
  { value: 'daily', label: 'Every day' },
  { value: 'weekly', label: 'Every week' },
  { value: 'monthly', label: 'Every month' },
]

const PRIORITY_STYLES = {
  low: 'bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400',
  medium: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400',
  high: 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400',
}

const COLUMNS = [
  { key: 'pending', label: 'To Do', icon: Circle, color: 'text-gray-400' },
  { key: 'in_progress', label: 'In Progress', icon: Clock3, color: 'text-amber-500' },
  { key: 'completed', label: 'Completed', icon: CheckCircle2, color: 'text-emerald-500' },
]

export default function Tasks() {
  const [tasks, setTasks] = useState([])
  const [members, setMembers] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', due_date: '', priority: 'medium', recurrence: '', assignee_id: '' })
  const [draggedId, setDraggedId] = useState(null)

  const load = () => getTasks().then(setTasks).catch(() => {})

  useEffect(() => {
    load()
    getMembers().then(setMembers).catch(() => {})
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) return
    await createTask({
      title: form.title,
      due_date: form.due_date || null,
      priority: form.priority,
      assignee_id: form.assignee_id || null,
      recurrence_rule: form.recurrence ? { freq: form.recurrence } : null,
    })
    setForm({ title: '', due_date: '', priority: 'medium', recurrence: '', assignee_id: '' })
    setShowForm(false)
    load()
  }

  const moveTask = async (task, newStatus) => {
    await updateTask(task.id, { status: newStatus })
    load()
  }

  const remove = async (id) => {
    await deleteTask(id)
    load()
  }

  const memberName = (id) => members.find((m) => m.id === id)?.name

  return (
    <div>
      <Topbar title="Tasks" breadcrumb="Workspace" />
      <div className="p-8 space-y-6">
        <div className="flex justify-end">
          <button onClick={() => setShowForm((s) => !s)} className="btn-primary flex items-center gap-2 text-sm">
            <Plus size={16} /> New Task
          </button>
        </div>

        <AnimatePresence>
          {showForm && (
            <motion.form
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              onSubmit={submit}
              className="premium-card p-5 space-y-3 overflow-hidden"
            >
              <input
                className="input-premium w-full"
                placeholder="Task title..."
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                autoFocus
              />
              <div className="flex flex-wrap gap-3">
                <input
                  type="date"
                  className="input-premium"
                  value={form.due_date}
                  onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                />
                <select className="input-premium" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
                <select className="input-premium" value={form.recurrence} onChange={(e) => setForm({ ...form, recurrence: e.target.value })}>
                  {RECURRENCE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
                <select className="input-premium" value={form.assignee_id} onChange={(e) => setForm({ ...form, assignee_id: e.target.value })}>
                  <option value="">Unassigned</option>
                  {members.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
                </select>
                <button className="ml-auto btn-primary text-sm">Add task</button>
              </div>
            </motion.form>
          )}
        </AnimatePresence>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {COLUMNS.map((col) => {
            const colTasks = tasks.filter((t) => t.status === col.key)
            const ColIcon = col.icon
            return (
              <div
                key={col.key}
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => {
                  if (draggedId) {
                    const task = tasks.find((t) => t.id === draggedId)
                    if (task && task.status !== col.key) moveTask(task, col.key)
                  }
                  setDraggedId(null)
                }}
                className="space-y-3"
              >
                <div className="flex items-center gap-2 px-1">
                  <ColIcon size={16} className={col.color} />
                  <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300">{col.label}</h3>
                  <span className="text-xs text-gray-400 badge bg-gray-100 dark:bg-gray-800">{colTasks.length}</span>
                </div>

                <div className="space-y-3 min-h-[80px]">
                  <AnimatePresence>
                    {colTasks.map((t) => (
                      <motion.div
                        key={t.id}
                        layout
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        draggable
                        onDragStart={() => setDraggedId(t.id)}
                        className="premium-card p-4 cursor-grab active:cursor-grabbing group"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className={`text-sm font-medium ${t.status === 'completed' ? 'line-through text-gray-400' : 'text-gray-800 dark:text-gray-200'}`}>
                            {t.title}
                          </p>
                          <button
                            onClick={() => remove(t.id)}
                            className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-500 transition-opacity"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                        <div className="flex flex-wrap items-center gap-1.5 mt-3">
                          <span className={`badge ${PRIORITY_STYLES[t.priority] || PRIORITY_STYLES.medium} capitalize`}>{t.priority}</span>
                          {t.due_date && <span className="badge bg-gray-100 dark:bg-gray-800 text-gray-500">{t.due_date}</span>}
                          {t.recurrence_rule && (
                            <span className="badge bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center gap-1">
                              <Repeat size={10} /> repeat
                            </span>
                          )}
                          {t.assignee_id && memberName(t.assignee_id) && (
                            <span className="badge bg-violet-50 dark:bg-violet-500/10 text-violet-600 dark:text-violet-400">
                              {memberName(t.assignee_id)}
                            </span>
                          )}
                        </div>
                        {col.key !== 'completed' && (
                          <div className="flex gap-2 mt-3">
                            {col.key === 'pending' && (
                              <button onClick={() => moveTask(t, 'in_progress')} className="text-xs text-amber-600 hover:underline">
                                Start →
                              </button>
                            )}
                            <button onClick={() => moveTask(t, 'completed')} className="text-xs text-emerald-600 hover:underline ml-auto">
                              Mark done
                            </button>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  {colTasks.length === 0 && (
                    <div className="border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-xl2 p-6 text-center text-xs text-gray-400">
                      Drop tasks here
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
