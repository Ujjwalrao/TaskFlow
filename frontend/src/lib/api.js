import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export default api

// Tasks
export const getTasks = () => api.get('/tasks').then((r) => r.data)
export const createTask = (payload) => api.post('/tasks', payload).then((r) => r.data)
export const updateTask = (id, payload) => api.patch(`/tasks/${id}`, payload).then((r) => r.data)
export const deleteTask = (id) => api.delete(`/tasks/${id}`).then((r) => r.data)

// Habits
export const getHabits = () => api.get('/habits').then((r) => r.data)
export const createHabit = (payload) => api.post('/habits', payload).then((r) => r.data)
export const logHabit = (id, date) => api.post(`/habits/${id}/log`, date ? { date } : {}).then((r) => r.data)
export const deleteHabit = (id) => api.delete(`/habits/${id}`).then((r) => r.data)

// Goals
export const getGoals = () => api.get('/goals').then((r) => r.data)
export const createGoal = (payload) => api.post('/goals', payload).then((r) => r.data)
export const deleteGoal = (id) => api.delete(`/goals/${id}`).then((r) => r.data)

// Workspace / team
export const getMembers = () => api.get('/workspace/members').then((r) => r.data)
export const addMember = (payload) => api.post('/workspace/members', payload).then((r) => r.data)
export const removeMember = (id, actingAs) => api.delete(`/workspace/members/${id}`, { params: { acting_as: actingAs } }).then((r) => r.data)
export const getTeamAnalytics = () => api.get('/workspace/analytics').then((r) => r.data)

// Search
export const semanticSearch = (q) => api.get('/search', { params: { q } }).then((r) => r.data)

// Feedback
export const sendFeedback = (payload) => api.post('/feedback', payload).then((r) => r.data)

// Notifications
export const saveTelegramConfig = (payload) => api.post('/notifications/telegram/config', payload).then((r) => r.data)
export const testTelegram = () => api.post('/notifications/telegram/test').then((r) => r.data)

// Google Calendar integration
export const googleStatus = () => api.get('/integrations/google/status').then((r) => r.data)
export const googleConnect = () => api.get('/integrations/google/connect').then((r) => r.data)
export const googleSync = () => api.post('/integrations/google/sync').then((r) => r.data)

// Push notifications
export const getVapidPublicKey = () => api.get('/notifications/push/vapid-public-key').then((r) => r.data)
export const subscribePush = (payload) => api.post('/notifications/push/subscribe', payload).then((r) => r.data)
export const testPush = () => api.post('/notifications/push/test').then((r) => r.data)

// Email digest
export const emailDigestStatus = () => api.get('/notifications/email-digest/status').then((r) => r.data)
export const sendEmailDigest = () => api.post('/notifications/email-digest/send').then((r) => r.data)

// Exports (return raw blob URLs)
export const exportPdfUrl = () => '/api/export/pdf'
export const exportCsvUrl = () => '/api/export/csv'
