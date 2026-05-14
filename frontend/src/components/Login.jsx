import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { loginUser } from '../api'

function parseAuthFromToken(token) {
  if (!token) {
    return { role: null, email: null }
  }

  try {
    const payload = token.split('.')[1]
    if (!payload) {
      return { role: null, email: null }
    }

    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    const decoded = JSON.parse(atob(padded))

    const rawRole = String(decoded.role || '').toLowerCase()
    const role = rawRole.includes('admin')
      ? 'admin'
      : rawRole.includes('evaluator')
        ? 'evaluator'
        : rawRole.includes('submitter')
          ? 'submitter'
          : null

    return {
      role,
      email: decoded.email || decoded.sub || null,
    }
  } catch {
    return { role: null, email: null }
  }
}

function Login() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const data = await loginUser(form)
      if (!data?.access_token) {
        throw new Error('Access token missing in response')
      }
      localStorage.setItem('access_token', data.access_token)
      if (data?.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }
      const parsed = parseAuthFromToken(data.access_token)
      if (parsed.role) {
        localStorage.setItem('user_role', parsed.role)
      }
      if (parsed.email) {
        localStorage.setItem('user_email', parsed.email)
      }
      setSuccess('Login successful. Tokens received from backend.')
      navigate('/')
    } catch (submitError) {
      const message = submitError?.response?.data?.detail || 'Login failed. Check credentials.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mx-auto mt-8 w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="text-2xl font-semibold text-slate-900">Login</h2>
      <p className="mt-2 text-slate-600">Authenticate using your backend /auth/login endpoint.</p>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>

      {error && <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
      {success && <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{success}</p>}

      <div className="mt-6 flex items-center justify-between">
        <Link to="/register" className="text-sm font-medium text-blue-600 hover:text-blue-800">
          Need an account? Register
        </Link>
        <Link
          to="/"
          className="inline-flex cursor-pointer rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          Back to Dashboard
        </Link>
      </div>
    </section>
  )
}

export default Login
