import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, ListTodo, Repeat, Target, Users,
  Search, FileDown, Bell, Settings as SettingsIcon,
  ChevronsLeft, ChevronsRight, Sparkles,
} from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/tasks', label: 'Tasks', icon: ListTodo },
  { to: '/habits', label: 'Habits', icon: Repeat },
  { to: '/goals', label: 'Goals', icon: Target },
  { to: '/team', label: 'Team', icon: Users },
  { to: '/search', label: 'Search', icon: Search },
  { to: '/reports', label: 'Reports', icon: FileDown },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <motion.aside
      animate={{ width: collapsed ? 84 : 260 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="shrink-0 h-screen sticky top-0 border-r border-gray-100 dark:border-gray-800/80
                 bg-white/80 dark:bg-surface-darkCard/80 backdrop-blur-xl flex flex-col z-20"
    >
      {/* Workspace switcher */}
      <div className="px-4 py-5 flex items-center gap-2.5 border-b border-gray-100 dark:border-gray-800/60">
        <div className="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center shrink-0 shadow-glow">
          <Sparkles size={18} className="text-white" />
        </div>
        <AnimatePresence initial={false}>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.15 }}
              className="overflow-hidden whitespace-nowrap"
            >
              <h1 className="text-base font-bold tracking-tight bg-gradient-to-r from-brand-600 to-accent-violet bg-clip-text text-transparent">
                TaskFlow
              </h1>
              <p className="text-[11px] text-gray-400">Personal Workspace</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
               transition-all duration-200 ${
                isActive
                  ? 'bg-brand-gradient text-white shadow-glow'
                  : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100/80 dark:hover:bg-gray-800/60 hover:text-gray-900 dark:hover:text-gray-100'
              }`
            }
          >
            <Icon size={18} className="shrink-0" />
            <AnimatePresence initial={false}>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="whitespace-nowrap overflow-hidden"
                >
                  {label}
                </motion.span>
              )}
            </AnimatePresence>
          </NavLink>
        ))}
      </nav>

      {/* User profile + notification badge */}
      <div className="px-3 py-4 border-t border-gray-100 dark:border-gray-800/60 space-y-3">
        <div className="flex items-center gap-2.5 px-2">
          <div className="relative shrink-0">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-400 to-accent-violet flex items-center justify-center text-white text-xs font-bold">
              Y
            </div>
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-accent-emerald text-white text-[9px] font-bold rounded-full flex items-center justify-center ring-2 ring-white dark:ring-surface-darkCard">
              <Bell size={9} />
            </span>
          </div>
          <AnimatePresence initial={false}>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="overflow-hidden whitespace-nowrap"
              >
                <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">You</p>
                <p className="text-[10px] text-gray-400">No sign-up · free</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button
          onClick={() => setCollapsed((c) => !c)}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-medium
                     text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/60 transition-colors"
        >
          {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
        </button>
      </div>
    </motion.aside>
  )
}
