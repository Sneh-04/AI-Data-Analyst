import api from './client.js'

const saveAuth = (data) => {
  localStorage.setItem('jwt', data.token)
  // Stored alongside the access token so client.js can silently renew the
  // session on a 401 instead of forcing the user back to the login page.
  localStorage.setItem('refreshToken', data.refreshToken)
  return data
}

export const register = (payload) =>
  api.post('/auth/register', payload).then((response) => saveAuth(response.data))

export const login = (payload) =>
  api.post('/auth/login', payload).then((response) => saveAuth(response.data))

export const logout = () => {
  const refreshToken = localStorage.getItem('refreshToken')
  localStorage.removeItem('jwt')
  localStorage.removeItem('refreshToken')
  if (!refreshToken) return Promise.resolve()
  // Best-effort: revoke server-side so the refresh token can't be replayed,
  // but logout must succeed locally even if this call fails (e.g. offline).
  return api.post('/auth/logout', { refreshToken }).catch(() => {})
}
