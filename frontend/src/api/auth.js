import api from './client.js'

const saveAuth = (data) => {
  localStorage.setItem('jwt', data.token)
  return data
}

export const register = (payload) =>
  api.post('/auth/register', payload).then((response) => saveAuth(response.data))

export const login = (payload) =>
  api.post('/auth/login', payload).then((response) => saveAuth(response.data))
