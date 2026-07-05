import { useState } from 'react'
import { Sun, Moon, Search, Plus, Bell } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTheme } from '../context/ThemeContext.jsx'
import { useNavigate } from 'react-router-dom'

export default function Topbar({ title, breadcrumb }) {
  const { isDark, toggleTheme } = useTheme()
  const [showNotif, setShowNotif] = useState(false)
  const navigate = useNavigate()

  return (
    <header className="flex items-center justify-between gap-4 px-8 py-5 border-b border-gray-100 dark:border-gray-800/80
                        bg-white/70 dark:bg-surface-dark/70 backdrop-blur-xl sticky top-0 z-10">
      <div>
        {breadcrumb && (
          <p className="text-xs text-gray-400 mb-0.5">{breadcrumb}</p>
        )}
        <h2 className="text-xl font-bold tracking-tight text-gray-900 dark:text-gray-100">{title}</h2>
      </div>

      <div className="flex-1 max-w-md hidden md:block">
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            onFocus={() => navigate('/search')}
            readOnly
            placeholder="Search anything..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700
                       bg-gray-50 dark:bg-gray-900/60 text-sm cursor-pointer
                       focus:outline-none focus:ring-2 focus:ring-brand-400/30"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => navigate('/tasks')}
          className="hidden sm:flex items-center gap-1.5 btn-primary text-sm py-2 px-3.5"
        >
          <Plus size={16} /> Quick Create
        </button>

        <div className="relative">
          <button
            onClick={() => setShowNotif((s) => !s)}
            className="relative p-2.5 rounded-xl border border-gray-200 dark:border-gray-700
                       bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <Bell size={16} className="text-gray-600 dark:text-gray-300" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-accent-emerald rounded-full ring-2 ring-white dark:ring-surface-dark" />
          </button>
          <AnimatePresence>
            {showNotif && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.97 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 mt-2 w-72 glass-card rounded-xl2 p-4 text-sm"
              >
                <p className="font-semibold text-gray-800 dark:text-gray-100 mb-2">Notifications</p>
                <p className="text-xs text-gray-400">You're all caught up 🎉</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button
          onClick={toggleTheme}
          aria-label="Toggle dark mode"
          className="p-2.5 rounded-xl border border-gray-200 dark:border-gray-700
                     bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          {isDark ? <Sun size={16} className="text-amber-400" /> : <Moon size={16} className="text-gray-600" />}
        </button>

        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-accent-violet flex items-center justify-center text-white text-xs font-bold cursor-pointer">
          Y
        </div>
      </div>
    </header>
  )
}
