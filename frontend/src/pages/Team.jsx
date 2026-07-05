import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Topbar from '../components/Topbar.jsx'
import { getMembers, addMember, removeMember, getTeamAnalytics } from '../lib/api.js'
import { Trash2, Users, Shield, Plus } from 'lucide-react'

export default function Team() {
  const [members, setMembers] = useState([])
  const [analytics, setAnalytics] = useState([])
  const [name, setName] = useState('')
  const [role, setRole] = useState('member')
  const [showForm, setShowForm] = useState(false)

  const load = () => {
    getMembers().then(setMembers).catch(() => {})
    getTeamAnalytics().then(setAnalytics).catch(() => {})
  }
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    if (!name.trim()) return
    await addMember({ name, role })
    setName('')
    setRole('member')
    setShowForm(false)
    load()
  }

  const remove = async (id) => {
    const admin = members.find((m) => m.role === 'admin')
    await removeMember(id, admin?.id)
    load()
  }

  return (
    <div>
      <Topbar title="Team" breadcrumb="Workspace" />
      <div className="p-8 space-y-6 max-w-4xl">
        <div className="glass-card rounded-xl2 p-4 text-sm text-brand-700 dark:text-brand-400 flex items-center gap-2">
          <Users size={16} />
          No login required — just add names to delegate tasks and see per-person progress.
        </div>

        <div className="flex justify-end">
          <button onClick={() => setShowForm((s) => !s)} className="btn-primary flex items-center gap-2 text-sm">
            <Plus size={16} /> Add Member
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
              <input className="input-premium flex-1" placeholder="Member name..." value={name} onChange={(e) => setName(e.target.value)} autoFocus />
              <select className="input-premium" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
              <button className="btn-primary text-sm">Add</button>
            </motion.form>
          )}
        </AnimatePresence>

        <div className="grid sm:grid-cols-2 gap-4">
          {analytics.map((m, i) => {
            const fullMember = members.find((mm) => mm.id === m.member_id)
            return (
              <motion.div
                key={m.member_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="premium-card p-5"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-11 h-11 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-soft"
                    style={{ background: `linear-gradient(135deg, ${m.color}, #8b5cf6)` }}
                  >
                    {m.name.slice(0, 1).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                      {m.name}
                      {fullMember?.role === 'admin' && (
                        <span className="badge bg-brand-50 text-brand-600 dark:bg-brand-500/10 flex items-center gap-1">
                          <Shield size={10} /> Admin
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-gray-400">
                      {m.completed_tasks}/{m.total_tasks} completed
                      {m.overdue_tasks > 0 && <span className="text-red-500"> · {m.overdue_tasks} overdue</span>}
                    </p>
                  </div>
                  <button onClick={() => remove(m.member_id)} className="text-gray-300 hover:text-red-500 transition-colors">
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="mt-4">
                  <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${m.completion_rate}%` }}
                      transition={{ duration: 0.8 }}
                      className="h-full bg-brand-gradient rounded-full"
                    />
                  </div>
                  <p className="text-[11px] text-gray-400 mt-1">{m.completion_rate}% completion rate</p>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
