import { motion } from 'framer-motion'
import Topbar from '../components/Topbar.jsx'
import { exportPdfUrl, exportCsvUrl } from '../lib/api.js'
import { FileText, Sheet } from 'lucide-react'

export default function Reports() {
  return (
    <div>
      <Topbar title="Reports" breadcrumb="Workspace" />
      <div className="p-8 max-w-2xl space-y-6">
        <p className="text-sm text-gray-400">Export your productivity data — generated locally, no external service involved.</p>

        <div className="grid sm:grid-cols-2 gap-5">
          <motion.a
            whileHover={{ y: -4 }}
            href={exportPdfUrl()}
            className="premium-card p-6 flex flex-col items-start gap-3"
          >
            <div className="w-11 h-11 rounded-xl bg-brand-gradient flex items-center justify-center shadow-glow">
              <FileText size={20} className="text-white" />
            </div>
            <div>
              <p className="font-semibold text-gray-900 dark:text-gray-100">Weekly PDF report</p>
              <p className="text-xs text-gray-400 mt-1">Task summary, team performance, habit streaks</p>
            </div>
          </motion.a>

          <motion.a
            whileHover={{ y: -4 }}
            href={exportCsvUrl()}
            className="premium-card p-6 flex flex-col items-start gap-3"
          >
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-glow">
              <Sheet size={20} className="text-white" />
            </div>
            <div>
              <p className="font-semibold text-gray-900 dark:text-gray-100">Tasks CSV export</p>
              <p className="text-xs text-gray-400 mt-1">Raw task data for spreadsheets/analysis</p>
            </div>
          </motion.a>
        </div>
      </div>
    </div>
  )
}
