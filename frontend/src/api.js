import axios from 'axios'

const http = axios.create({ baseURL: '/api/v1', timeout: 20000 })

// Surface backend error messages (FastAPI `detail`) to a global toast handler.
http.interceptors.response.use(
  (r) => r,
  (err) => {
    const detail = err?.response?.data?.detail
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg).join('; ')
      : detail || err.message || '请求失败'
    if (window.__libuToast) window.__libuToast(msg, 'error')
    return Promise.reject(err)
  }
)

// ----- money helpers (backend stores integer cents) -----
export const toYuan = (cents) => (cents == null ? '0.00' : (cents / 100).toFixed(2))
export const toCents = (yuan) => Math.round(parseFloat(yuan || '0') * 100)

export const api = {
  meta: () => http.get('/meta').then((r) => r.data),

  members: (includeInactive = false) =>
    http.get('/members', { params: { include_inactive: includeInactive } }).then((r) => r.data),
  createMember: (data) => http.post('/members', data).then((r) => r.data),
  updateMember: (id, data) => http.patch(`/members/${id}`, data).then((r) => r.data),
  deleteMember: (id) => http.delete(`/members/${id}`).then((r) => r.data),

  counterparties: (params = {}) => http.get('/counterparties', { params }).then((r) => r.data),
  counterparty: (id) => http.get(`/counterparties/${id}`).then((r) => r.data),
  createCounterparty: (data) => http.post('/counterparties', data).then((r) => r.data),
  updateCounterparty: (id, data) => http.patch(`/counterparties/${id}`, data).then((r) => r.data),
  deleteCounterparty: (id) => http.delete(`/counterparties/${id}`).then((r) => r.data),
  convertToHousehold: (id, data) =>
    http.post(`/counterparties/${id}/convert-to-household`, data).then((r) => r.data),
  merge: (id, data) => http.post(`/counterparties/${id}/merge`, data).then((r) => r.data),

  tags: () => http.get('/tags').then((r) => r.data),

  events: (params = {}) => http.get('/events', { params }).then((r) => r.data),
  event: (id) => http.get(`/events/${id}`).then((r) => r.data),
  createEvent: (data) => http.post('/events', data).then((r) => r.data),
  updateEvent: (id, data) => http.patch(`/events/${id}`, data).then((r) => r.data),
  deleteEvent: (id) => http.delete(`/events/${id}`).then((r) => r.data),
  addRecords: (eventId, records) =>
    http.post(`/events/${eventId}/records`, { records }).then((r) => r.data),

  deleteRecord: (id) => http.delete(`/records/${id}`).then((r) => r.data),

  ledger: (params = {}) => http.get('/gifts/ledger', { params }).then((r) => r.data),
  ledgerDetail: (id) => http.get(`/gifts/ledger/${id}`).then((r) => r.data),

  overview: (params = {}) => http.get('/stats/overview', { params }).then((r) => r.data),
  trend: (params = {}) => http.get('/stats/trend', { params }).then((r) => r.data),
  byMember: () => http.get('/stats/by-member').then((r) => r.data),
}
