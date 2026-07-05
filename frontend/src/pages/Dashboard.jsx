import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import Topbar from '../components/Topbar.jsx'
import { getTasks, getHabits, getGoals } from '../lib/api.js'
import { CheckCircle2, Clock, Flame, Target, TrendingUp } from 'lucide-react'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
}
const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
}

function StatCard({ icon: Icon, label, value, gradient }) {
  return (
    <motion.div variants={item} className="premium-card p-5 flex items-center gap-4">
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center bg-gradient-to-br ${gradient} shadow-soft`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <motion.p
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
          className="text-2xl font-extrabold text-gray-900 dark:text-gray-100"
        >
          {value}
        </motion.p>
        <p className="text-xs text-gray-400 font-medium">{label}</p>
      </div>
    </motion.div>
  )
}

function ProgressRing({ percent, label }) {
  const r = 34
  const c = 2 * Math.PI * r
  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="88" height="88" className="-rotate-90">
        <circle cx="44" cy="44" r={r} stroke="currentColor" strokeWidth="8" fill="none" className="text-gray-100 dark:text-gray-800" />
        <motion.circle
          cx="44" cy="44" r={r} stroke="url(#grad)" strokeWidth="8" fill="none" strokeLinecap="round"
          initial={{ strokeDasharray: c, strokeDashoffset: c }}
          animate={{ strokeDashoffset: c - (percent / 100) * c }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
        <defs>
          <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
      </svg>
      <div className="-mt-16 text-center">
        <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{percent}%</p>
      </div>
      <p className="text-xs text-gray-400 mt-8">{label}</p>
    </div>
  )
}

export default function Dashboard() {
  const [tasks, setTasks] = useState([])
  const [habits, setHabits] = useState([])
  const [goals, setGoals] = useState([])

  useEffect(() => {
    getTasks().then(setTasks).catch(() => {})
    getHabits().then(setHabits).catch(() => {})
    getGoals().then(setGoals).catch(() => {})
  }, [])

  const completed = tasks.filter((t) => t.status === 'completed').length
  const pending = tasks.filter((t) => t.status !== 'completed').length
  const overdue = tasks.filter(
    (t) => t.status !== 'completed' && t.due_date && t.due_date < new Date().toISOString().slice(0, 10)
  ).length
  const bestStreak = habits.reduce((m, h) => Math.max(m, h.current_streak || 0), 0)
  const total = completed + pending
  const productivityScore = total ? Math.round((completed / total) * 100) : 0

  const pieData = [
    { name: 'Completed', value: completed || 0.001, color: '#10b981' },
    { name: 'Pending', value: pending || 0.001, color: '#f59e0b' },
  ]

  return (
    <div>
      <Topbar title="Dashboard" breadcrumb="Overview" />
      <div className="p-8 space-y-8">
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          <StatCard icon={CheckCircle2} label="Completed tasks" value={completed} gradient="from-emerald-400 to-emerald-600" />
          <StatCard icon={Clock} label="Pending tasks" value={pending} gradient="from-amber-400 to-amber-600" />
          <StatCard icon={Flame} label="Best habit streak" value={bestStreak} gradient="from-rose-400 to-rose-600" />
          <StatCard icon={Target} label="Active goals" value={goals.length} gradient="from-brand-400 to-accent-violet" />
        </motion.div>

        {overdue > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50/80 dark:bg-red-500/10 border border-red-200/60 dark:border-red-500/20
                       text-red-700 dark:text-red-400 rounded-xl2 px-5 py-4 text-sm font-medium backdrop-blur"
          >
            ⚠️ You have {overdue} overdue task{overdue > 1 ? 's' : ''}. Check the Tasks page.
          </motion.div>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="premium-card p-6 lg:col-span-2"
          >
            <h3 className="font-bold mb-4 text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <TrendingUp size={18} className="text-brand-500" /> Upcoming tasks
            </h3>
            {tasks.filter((t) => t.status !== 'completed').slice(0, 6).length === 0 ? (
              <p className="text-sm text-gray-400">No pending tasks — you're all caught up.</p>
            ) : (
              <ul className="divide-y divide-gray-100 dark:divide-gray-800/60">
                {tasks
                  .filter((t) => t.status !== 'completed')
                  .slice(0, 6)
                  .map((t, i) => (
                    <motion.li
                      key={t.id}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.05 * i }}
                      className="py-3 flex items-center justify-between text-sm group"
                    >
                      <span className="text-gray-700 dark:text-gray-300 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                        {t.title}
                      </span>
                      <span className="text-xs text-gray-400 badge bg-gray-100 dark:bg-gray-800">{t.due_date || 'No due date'}</span>
                    </motion.li>
                  ))}
              </ul>
            )}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="premium-card p-6 flex flex-col items-center justify-center gap-4"
          >
            <h3 className="font-bold text-gray-900 dark:text-gray-100 self-start">Productivity Score</h3>
            <ProgressRing percent={productivityScore} label="Completion rate" />
            {total > 0 && (
              <div className="w-full h-24 -mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} dataKey="value" innerRadius={22} outerRadius={36} paddingAngle={4}>
                      {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
}
