import axios from 'axios'

// Every call goes through Spring Boot (auth, persistence, audit log),
// never straight to the FastAPI ML service from the browser.
const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const datasetApi = {
  clean: (id, payload) => api.post(`/datasets/${id}/clean`, payload).then(r => r.data),
  healthScore: (id, payload) => api.post(`/datasets/${id}/health-score`, payload).then(r => r.data),
  forecast: (id, payload) => api.post(`/datasets/${id}/forecast`, payload).then(r => r.data),
  insights: (id, payload) => api.post(`/datasets/${id}/insights`, payload).then(r => r.data),
  chat: (id, payload) => api.post(`/datasets/${id}/chat`, payload).then(r => r.data),
}

export default api
