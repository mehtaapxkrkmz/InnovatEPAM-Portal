import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
})


export const fetchIdeas = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await api.get('/ideas', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    return response.data
  } catch (error) {
    console.error("API Error:", error)
    throw error
  }
}

export const patchIdeaStatus = async (ideaId, payload) => {
  const token = localStorage.getItem('access_token')
  const response = await api.patch(`/ideas/${ideaId}/status`, payload, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  return response.data
}

export const loginUser = async (payload) => {
  const response = await api.post('/auth/login', payload)
  return response.data
}

export const registerUser = async (payload) => {
  const response = await api.post('/auth/register', payload)
  return response.data
}

export const createIdea = async (formData) => {
  const token = localStorage.getItem('access_token')
  const response = await api.post('/ideas', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  return response.data
}

export default api