import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
})


export const fetchIdeas = async () => {
  try {
    const response = await api.get('/ideas')
    return response.data
  } catch (error) {
    console.error("API Error:", error)
    throw error
  }
}

export const patchIdeaStatus = async (ideaId, payload) => {
  const response = await api.patch(`/ideas/${ideaId}/status`, payload)
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
  const response = await api.post('/ideas', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export default api