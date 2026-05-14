import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createIdea } from '../api'

const categoryOptions = ['Product', 'Process', 'Cost-Savings', 'Customer-Experience']
const priorityOptions = ['LOW', 'MEDIUM', 'HIGH']
const MAX_FILES = 3

function getFileTypeKind(fileName) {
  const extension = (fileName.split('.').pop() || '').toLowerCase()

  if (extension === 'pdf') return 'pdf'
  if (['png', 'jpg', 'jpeg'].includes(extension)) return 'image'
  if (['doc', 'docx'].includes(extension)) return 'doc'
  return 'file'
}

function getFileBadge(kind) {
  if (kind === 'pdf') return 'PDF'
  if (kind === 'image') return 'IMG'
  if (kind === 'doc') return 'DOC'
  return 'FILE'
}

function getFileBadgeClass(kind) {
  if (kind === 'pdf') return 'bg-rose-100 text-rose-700 ring-rose-200'
  if (kind === 'image') return 'bg-emerald-100 text-emerald-700 ring-emerald-200'
  if (kind === 'doc') return 'bg-sky-100 text-sky-700 ring-sky-200'
  return 'bg-slate-100 text-slate-700 ring-slate-200'
}

function buildFileKey(file) {
  return `${file.name}:${file.size}:${file.lastModified}`
}

function SubmitIdea() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'Product',
    priority: 'MEDIUM',
    estimated_budget: '',
    files: [],
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [uploadWarning, setUploadWarning] = useState('')
  const [submitIntent, setSubmitIntent] = useState('submitted')

  const handleChange = (event) => {
    const { name, value, files, type } = event.target
    if (type === 'file') {
      const incomingFiles = files ? Array.from(files) : []
      setForm((prev) => {
        const merged = [...prev.files]
        const existingKeys = new Set(prev.files.map(buildFileKey))

        incomingFiles.forEach((file) => {
          const key = buildFileKey(file)
          if (!existingKeys.has(key)) {
            merged.push(file)
            existingKeys.add(key)
          }
        })

        if (merged.length > MAX_FILES) {
          setUploadWarning(`You can upload up to ${MAX_FILES} files. Extra files were not added.`)
        } else {
          setUploadWarning('')
        }

        return { ...prev, files: merged.slice(0, MAX_FILES) }
      })
      event.target.value = ''
      return
    }

    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    setUploadWarning('')

    try {
      const formData = new FormData()
      formData.append('title', form.title)
      formData.append('description', form.description)
      formData.append('category', form.category)
      formData.append('priority', form.priority)
      formData.append('estimated_budget', String(form.estimated_budget || 0))
      formData.append('initial_status', submitIntent)
      form.files.forEach((file) => formData.append('files', file))

      await createIdea(formData)
      setSuccess(
        submitIntent === 'draft'
          ? 'Draft saved! Redirecting to dashboard...'
          : 'Idea submitted successfully. Redirecting to dashboard...'
      )
      setTimeout(() => navigate('/'), 1200)
    } catch (submitError) {
      const message = submitError?.response?.data?.detail || 'Idea submission failed. Please try again.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const removeSelectedFile = (indexToRemove) => {
    setForm((prev) => ({
      ...prev,
      files: prev.files.filter((_, index) => index !== indexToRemove),
    }))
    setUploadWarning('')
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
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="files">
            Attachments (optional)
          </label>
          <input
            id="files"
            name="files"
            type="file"
            multiple
            onChange={handleChange}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          />
          <p className="mt-1 text-xs text-slate-500">Supported: PDF, PNG, JPG, TXT. Max 5MB each, up to 3 files.</p>

          {uploadWarning && (
            <p className="mt-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">{uploadWarning}</p>
          )}

          {form.files.length > 0 && (
            <div className="mt-3 space-y-2">
              {form.files.map((file, index) => {
                const fileKind = getFileTypeKind(file.name)
                const badgeClass = getFileBadgeClass(fileKind)

                return (
                  <div
                    key={buildFileKey(file)}
                    className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2"
                  >
                    <div className="flex min-w-0 items-center gap-2">
                      <span
                        className={`inline-flex h-6 min-w-10 items-center justify-center rounded-md px-2 text-[10px] font-semibold ring-1 ${badgeClass}`}
                      >
                        {getFileBadge(fileKind)}
                      </span>
                      <span className="truncate text-sm text-slate-700" title={file.name}>
                        {file.name}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeSelectedFile(index)}
                      className="inline-flex h-6 w-6 items-center justify-center rounded-md border border-slate-300 text-xs font-semibold text-slate-500 transition hover:border-rose-300 hover:bg-rose-50 hover:text-rose-600"
                      aria-label={`Remove ${file.name}`}
                    >
                      X
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="mt-2 flex gap-3">
          <button
            type="submit"
            disabled={loading}
            onClick={() => setSubmitIntent('submitted')}
            className="flex-1 inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading && submitIntent === 'submitted' ? 'Submitting...' : 'Submit Idea'}
          </button>
          <button
            type="submit"
            disabled={loading}
            onClick={() => setSubmitIntent('draft')}
            className="flex-1 inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading && submitIntent === 'draft' ? 'Saving...' : 'Save as Draft'}
          </button>
        </div>
      </form>

      {error && <p className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
      {success && <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{success}</p>}
    </section>
  )
}

export default SubmitIdea
