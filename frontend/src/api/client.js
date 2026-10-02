import axios from 'axios'

// Every call goes through Spring Boot (auth, persistence, audit log),
// never straight to the FastAPI ML service from the browser.
const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Fixes the "expired token stays in localStorage" gap: previously a 401 from
// an expired access token just surfaced as a failed request with no recovery,
// even though ProtectedRoute only checks token *presence*, not validity. Now
// a single 401 triggers one silent refresh-and-retry before giving up.
let refreshInFlight = null

function clearSessionAndRedirect() {
  localStorage.removeItem('jwt')
  localStorage.removeItem('refreshToken')
  window.location.hash = '#/login'
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    const isAuthEndpoint = config?.url?.startsWith('/auth/')
    if (response?.status !== 401 || isAuthEndpoint || config._retried) {
      return Promise.reject(error)
    }

    const refreshToken = localStorage.getItem('refreshToken')
    if (!refreshToken) {
      clearSessionAndRedirect()
      return Promise.reject(error)
    }

    config._retried = true
    try {
      // Coalesce concurrent 401s into a single refresh call instead of one
      // refresh-and-rotate per failed request (rotation revokes the old
      // token, so a second concurrent refresh with the same old token would
      // otherwise fail).
      if (!refreshInFlight) {
        refreshInFlight = axios
          .post('/api/auth/refresh', { refreshToken })
          .finally(() => { refreshInFlight = null })
      }
      const { data } = await refreshInFlight
      localStorage.setItem('jwt', data.token)
      localStorage.setItem('refreshToken', data.refreshToken)
      config.headers.Authorization = `Bearer ${data.token}`
      return api(config)
    } catch (refreshError) {
      clearSessionAndRedirect()
      return Promise.reject(refreshError)
    }
  }
)

export const datasetApi = {
  clean: (id, payload) => api.post(`/datasets/${id}/clean`, payload).then(r => r.data),
  healthScore: (id, payload) => api.post(`/datasets/${id}/health-score`, payload).then(r => r.data),
  forecast: (id, payload) => api.post(`/datasets/${id}/forecast`, payload).then(r => r.data),
  insights: (id, payload) => api.post(`/datasets/${id}/insights`, payload).then(r => r.data),
  chat: (id, payload) => api.post(`/datasets/${id}/chat`, payload).then(r => r.data),
}

export default api
