import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createIdea } from '../api'

const categoryOptions = ['Product', 'Process', 'Cost-Savings', 'Customer-Experience']
const priorityOptions = ['LOW', 'MEDIUM', 'HIGH']

function SubmitIdea() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'Product',
    priority: 'MEDIUM',
    estimated_budget: '',
    attachment: null,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (event) => {
    const { name, value, files, type } = event.target
    if (type === 'file') {
      setForm((prev) => ({ ...prev, attachment: files && files[0] ? files[0] : null }))
      return
    }

    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const formData = new FormData()
      formData.append('title', form.title)
      formData.append('description', form.description)
      formData.append('category', form.category)
      formData.append('priority', form.priority)
      formData.append('estimated_budget', String(form.estimated_budget || 0))
      if (form.attachment) {
        formData.append('attachment', form.attachment)
      }

      await createIdea(formData)
      setSuccess('Idea submitted successfully. Redirecting to dashboard...')
      setTimeout(() => navigate('/'), 1200)
    } catch (submitError) {
      const message = submitError?.response?.data?.detail || 'Idea submission failed. Please try again.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mx-auto mt-8 w-full max-w-3xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="mb-6 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Submit New Idea</h2>
          <p className="mt-1 text-slate-600">Add a new innovation idea to the platform.</p>
        </div>
        <Link
          to="/"
          className="inline-flex cursor-pointer rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          Back to Dashboard
        </Link>
      </div>

      <form className="grid gap-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="title">
            Title
          </label>
          <input
            id="title"
            name="title"
            type="text"
            value={form.title}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="description">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            rows={5}
            value={form.description}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="category">
              Category
            </label>
            <select
              id="category"
              name="category"
              value={form.category}
              onChange={handleChange}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            >
              {categoryOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="priority">
              Priority
            </label>
            <select
              id="priority"
              name="priority"
              value={form.priority}
              onChange={handleChange}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            >
              {priorityOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="estimated_budget">
            Estimated Budget
          </label>
          <input
            id="estimated_budget"
            name="estimated_budget"
            type="number"
            min="0"
            step="1"
            value={form.estimated_budget}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="attachment">
            Attachment (optional)
          </label>
          <input
            id="attachment"
            name="attachment"
            type="file"
            onChange={handleChange}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
          <p className="mt-1 text-xs text-slate-500">Supported: PDF, PNG, JPG, TXT. Max 5MB.</p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="mt-2 inline-flex w-full items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Submitting...' : 'Submit Idea'}
        </button>
      </form>

      {error && <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
      {success && <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{success}</p>}
    </section>
  )
}

export default SubmitIdea
