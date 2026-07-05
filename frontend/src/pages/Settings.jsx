import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Topbar from '../components/Topbar.jsx'
import { useTheme } from '../context/ThemeContext.jsx'
import {
  saveTelegramConfig, testTelegram, googleStatus, googleConnect, googleSync,
  getVapidPublicKey, subscribePush, testPush, emailDigestStatus, sendEmailDigest,
} from '../lib/api.js'
import { Send, ExternalLink, Calendar, RefreshCw, Bell, Mail, Sun, Moon, Palette, Plug } from 'lucide-react'

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)))
}

const TABS = [
  { key: 'notifications', label: 'Notifications', icon: Bell },
  { key: 'integrations', label: 'Integrations', icon: Plug },
  { key: 'appearance', label: 'Appearance', icon: Palette },
]

export default function Settings() {
  const [activeTab, setActiveTab] = useState('notifications')
  const { isDark, toggleTheme } = useTheme()

  const [botToken, setBotToken] = useState('')
  const [chatId, setChatId] = useState('')
  const [status, setStatus] = useState('')
  const [gStatus, setGStatus] = useState({ configured: false, connected: false })
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState('')
  const [pushMsg, setPushMsg] = useState('')
  const [digestStatus, setDigestStatus] = useState({ configured: false })
  const [digestMsg, setDigestMsg] = useState('')

  useEffect(() => {
    googleStatus().then(setGStatus).catch(() => {})
    emailDigestStatus().then(setDigestStatus).catch(() => {})
  }, [])

  const sendDigest = async () => {
    setDigestMsg('Sending...')
    try {
      const res = await sendEmailDigest()
      setDigestMsg(res.sent ? 'Digest email sent!' : `Failed: ${res.reason}`)
    } catch {
      setDigestMsg('Failed to send digest.')
    }
  }

  const enablePush = async () => {
    try {
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        setPushMsg('Push not supported in this browser.')
        return
      }
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') {
        setPushMsg('Permission denied.')
        return
      }
      const reg = await navigator.serviceWorker.ready
      const { public_key } = await getVapidPublicKey()
      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(public_key),
      })
      await subscribePush({ member_id: 'default', subscription })
      setPushMsg('Push notifications enabled!')
    } catch (err) {
      setPushMsg('Could not enable push: ' + err.message)
    }
  }

  const sendTestPush = async () => {
    await testPush()
    setPushMsg('Test notification sent.')
  }

  const connectGoogle = async () => {
    const res = await googleConnect()
    if (res.auth_url) window.location.href = res.auth_url
  }

  const syncGoogle = async () => {
    setSyncing(true)
    try {
      const res = await googleSync()
      setSyncMsg(`Synced ${res.synced_count} task(s) to Google Calendar.`)
    } catch {
      setSyncMsg('Sync failed — check connection.')
    } finally {
      setSyncing(false)
    }
  }

  const save = async (e) => {
    e.preventDefault()
    await saveTelegramConfig({ bot_token: botToken, chat_id: chatId })
    setStatus('Saved. Sending a test message...')
    try {
      const res = await testTelegram()
      setStatus(res.sent ? 'Test message sent — check Telegram!' : 'Could not send — check token/chat ID.')
    } catch {
      setStatus('Could not send — check token/chat ID.')
    }
  }

  return (
    <div>
      <Topbar title="Settings" breadcrumb="Workspace" />
      <div className="p-8 max-w-2xl space-y-6">
        <div className="flex gap-1.5 p-1 bg-gray-100 dark:bg-gray-900 rounded-xl w-fit">
          {TABS.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.key
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'text-white' : 'text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                }`}
              >
                {isActive && (
                  <motion.div layoutId="settings-tab" className="absolute inset-0 bg-brand-gradient rounded-lg shadow-glow" />
                )}
                <span className="relative flex items-center gap-2">
                  <Icon size={15} /> {tab.label}
                </span>
              </button>
            )
          })}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.15 }}
            className="space-y-6"
          >
            {activeTab === 'notifications' && (
              <>
                <section className="premium-card p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">Telegram Notifications</h3>
                  <p className="text-xs text-gray-400 mb-4">Free forever. Message @BotFather on Telegram, create a bot, and paste the token below.</p>
                  <form onSubmit={save} className="space-y-3">
                    <input className="input-premium w-full" placeholder="Bot token" value={botToken} onChange={(e) => setBotToken(e.target.value)} />
                    <input className="input-premium w-full" placeholder="Chat ID" value={chatId} onChange={(e) => setChatId(e.target.value)} />
                    <button className="btn-primary text-sm flex items-center gap-2"><Send size={16} /> Save & test</button>
                    {status && <p className="text-xs text-gray-500">{status}</p>}
                  </form>
                </section>

                <section className="premium-card p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2"><Mail size={18} /> Email Digest</h3>
                  <p className="text-xs text-gray-400 mb-3">Weekly summary email via Resend's free tier (100 emails/day, no credit card).</p>
                  {!digestStatus.configured && (
                    <p className="text-xs text-gray-400">Add <code>RESEND_API_KEY</code> and <code>DIGEST_TO_EMAIL</code> to your backend <code>.env</code> first.</p>
                  )}
                  {digestStatus.configured && <button onClick={sendDigest} className="btn-primary text-sm">Send weekly digest now</button>}
                  {digestMsg && <p className="text-xs text-gray-500 mt-2">{digestMsg}</p>}
                </section>

                <section className="premium-card p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2"><Bell size={18} /> Browser Push Notifications</h3>
                  <p className="text-xs text-gray-400 mb-3">Free, native browser notifications — no third-party service, works even without Telegram.</p>
                  <div className="flex gap-3">
                    <button onClick={enablePush} className="btn-primary text-sm">Enable push notifications</button>
                    <button onClick={sendTestPush} className="btn-ghost text-sm">Send test</button>
                  </div>
                  {pushMsg && <p className="text-xs text-gray-500 mt-2">{pushMsg}</p>}
                </section>
              </>
            )}

            {activeTab === 'integrations' && (
              <>
                <section className="premium-card p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2"><Calendar size={18} /> Google Calendar</h3>
                  {!gStatus.configured && (
                    <p className="text-xs text-gray-400 mb-3">Not set up yet. Add <code>GOOGLE_CLIENT_ID</code> and <code>GOOGLE_CLIENT_SECRET</code> to your backend <code>.env</code> file first.</p>
                  )}
                  {gStatus.configured && !gStatus.connected && (
                    <button onClick={connectGoogle} className="btn-primary text-sm">Connect Google Calendar</button>
                  )}
                  {gStatus.connected && (
                    <div className="space-y-2">
                      <p className="text-xs text-emerald-600 font-medium">✅ Connected</p>
                      <button onClick={syncGoogle} disabled={syncing} className="btn-primary text-sm flex items-center gap-2">
                        <RefreshCw size={16} className={syncing ? 'animate-spin' : ''} />
                        {syncing ? 'Syncing...' : 'Sync tasks to calendar'}
                      </button>
                      {syncMsg && <p className="text-xs text-gray-500">{syncMsg}</p>}
                    </div>
                  )}
                </section>

                <section className="premium-card p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">Other Integrations</h3>
                  <p className="text-xs text-gray-400 mb-4">These require you to register your own app with the provider (free), then plug in the client ID/secret here.</p>
                  <ul className="space-y-2 text-sm">
                    {['Outlook Calendar', 'Notion', 'Slack', 'Jira'].map((name) => (
                      <li key={name} className="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                        <span className="text-gray-700 dark:text-gray-300">{name}</span>
                        <span className="text-xs text-gray-400 flex items-center gap-1">Not connected <ExternalLink size={12} /></span>
                      </li>
                    ))}
                  </ul>
                </section>
              </>
            )}

            {activeTab === 'appearance' && (
              <section className="premium-card p-6">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">Theme</h3>
                <p className="text-xs text-gray-400 mb-4">Choose between light and dark mode. Defaults to a clean, white theme.</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => isDark && toggleTheme()}
                    className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-colors ${
                      !isDark ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10' : 'border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <Sun size={20} className="text-amber-500" />
                    <span className="text-sm font-medium">Light</span>
                  </button>
                  <button
                    onClick={() => !isDark && toggleTheme()}
                    className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-colors ${
                      isDark ? 'border-brand-500 bg-brand-500/10' : 'border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <Moon size={20} className="text-indigo-400" />
                    <span className="text-sm font-medium">Dark</span>
                  </button>
                </div>
              </section>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
