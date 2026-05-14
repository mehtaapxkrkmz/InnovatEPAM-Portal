import { useEffect, useMemo, useState } from 'react'
import { Link, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { fetchIdeas, patchIdeaStatus } from './api'
import Login from './components/Login'
import Register from './components/Register'
import SubmitIdea from './components/SubmitIdea'

const priorityBadgeClass = {
  HIGH: 'bg-red-100 text-red-700 ring-red-200',
  MEDIUM: 'bg-amber-100 text-amber-700 ring-amber-200',
  LOW: 'bg-emerald-100 text-emerald-700 ring-emerald-200',
}

const statusBadgeClass = {
  draft: 'bg-slate-100 text-slate-600 ring-slate-300',
  submitted: 'bg-amber-100 text-amber-700 ring-amber-200',
  under_review: 'bg-sky-100 text-sky-700 ring-sky-200',
  accepted: 'bg-emerald-100 text-emerald-700 ring-emerald-200',
  rejected: 'bg-rose-100 text-rose-700 ring-rose-200',
}

const statusActionButtons = [
  { label: 'Under Review', value: 'under_review', className: 'bg-sky-600 hover:bg-sky-700' },
  { label: 'Accepted', value: 'accepted', className: 'bg-emerald-600 hover:bg-emerald-700' },
  { label: 'Rejected', value: 'rejected', className: 'bg-rose-600 hover:bg-rose-700' },
]

function formatBudget(value) {
  if (value === null || value === undefined) return 'Not specified'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value)
}

function formatStatus(status) {
  return String(status || 'submitted').replaceAll('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function resolveAttachmentUrl(attachmentUrl) {
  if (!attachmentUrl) {
    return null
  }
  if (attachmentUrl.startsWith('http://') || attachmentUrl.startsWith('https://')) {
    return attachmentUrl
  }
  const normalized = attachmentUrl.startsWith('/') ? attachmentUrl : `/${attachmentUrl}`
  return `http://127.0.0.1:8000${normalized}`
}

function isImageAttachment(url) {
  if (!url) {
    return false
  }
  return /\.(png|jpe?g|gif|webp|bmp|svg)$/i.test(url)
}

function parseAuthFromToken(token) {
  if (!token) {
    return { label: 'User', role: null }
  }

  try {
    const payload = token.split('.')[1]
    if (!payload) {
      return { label: 'User', role: null }
    }

    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    const decoded = JSON.parse(atob(padded))

    const rawIdentity = decoded.email || decoded.sub || 'User'
    const label = typeof rawIdentity === 'string' && rawIdentity.includes('@')
      ? rawIdentity.split('@')[0]
      : rawIdentity

    const rawRole = String(decoded.role || '').toLowerCase()
    const role = rawRole.includes('admin')
      ? 'admin'
      : rawRole.includes('evaluator')
        ? 'evaluator'
        : rawRole.includes('submitter')
          ? 'submitter'
          : null

    return { label, role }
  } catch {
    return { label: 'User', role: null }
  }
}

function DashboardContent({
  ideas,
  loading,
  error,
  summary,
  expandedCards,
  onToggleCard,
  onUpdateStatus,
  updatingIdeaId,
  canManageStatus,
  commentInputs,
  onCommentChange,
  scoreInputs,
  onScoreChange,
  userEmail,
  isLoggedIn,
  userRole,
}) {
  return (
    <>
      <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-sm text-slate-500">Home / Dashboard</p>
        <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-2xl font-semibold text-slate-900">All Ideas on One Screen</h2>
          <div className="flex items-center gap-3">
            {canManageStatus && (
              <span className="inline-flex items-center gap-1.5 rounded-lg bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800 ring-1 ring-amber-200">
                <span aria-hidden="true">🔍</span>
                Blind Review Mode Active
              </span>
            )}
            <span className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white">
              Total Ideas: {ideas.length}
            </span>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <article className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm text-slate-500">High Priority</p>
          <p className="mt-2 text-2xl font-bold text-red-600">{summary.high}</p>
        </article>
        <article className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm text-slate-500">Medium Priority</p>
          <p className="mt-2 text-2xl font-bold text-amber-600">{summary.medium}</p>
        </article>
        <article className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm text-slate-500">Low Priority</p>
          <p className="mt-2 text-2xl font-bold text-emerald-600">{summary.low}</p>
        </article>
      </section>

      {loading && (
        <div className="mt-8 rounded-2xl bg-white p-8 text-center text-slate-600 shadow-sm ring-1 ring-slate-200">
          Loading ideas...
        </div>
      )}

      {!loading && error && (
        <div className="mt-8 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700 text-center">
          {error}
          <p className="mt-2 text-xs text-red-500">Check: Is FastAPI running on 127.0.0.1:8000?</p>
        </div>
      )}

      {!loading && !error && ideas.length === 0 && (
        <div className="mt-8 rounded-2xl bg-white p-8 text-center text-slate-600 shadow-sm ring-1 ring-slate-200">
          No ideas found in the database.
        </div>
      )}

      {!loading && !error && ideas.length > 0 && (
        <section className="mt-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {ideas.map((idea) => {
            const priority = (idea.priority || 'MEDIUM').toUpperCase()
            const badgeClass = priorityBadgeClass[priority] || priorityBadgeClass.MEDIUM
            const status = String(idea.status || 'submitted').toLowerCase()
            const statusClass = statusBadgeClass[status] || statusBadgeClass.submitted
            const isExpanded = expandedCards.has(idea.id)
            const isDraft = status === 'draft'
            const isOwner = isLoggedIn && idea.created_by === userEmail
            const attachmentUrls = Array.isArray(idea.attachment_urls)
              ? idea.attachment_urls
              : idea.attachment_url
                ? [idea.attachment_url]
                : []
            const isUpdating = updatingIdeaId === idea.id

            return (
              <article
                key={idea.id}
                className="flex h-full cursor-pointer flex-col rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 transition-shadow hover:shadow-md"
                onClick={() => onToggleCard(idea.id)}
              >
                <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
                  <h2 className="line-clamp-2 text-lg font-semibold text-slate-900">{idea.title}</h2>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${statusClass}`}
                    >
                      {formatStatus(status)}
                    </span>
                    <span
                      className={`inline-flex shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${badgeClass}`}
                    >
                      {priority}
                    </span>
                  </div>
                </div>

                <p className={`mb-4 text-sm leading-6 text-slate-600 ${isExpanded ? '' : 'line-clamp-4'}`}>
                  {idea.description}
                </p>

                <div className="mt-auto space-y-2 border-t border-slate-100 pt-4 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Creator</span>
                    <span className="font-semibold text-slate-900">
                      {canManageStatus && !isOwner ? 'Anonymous User' : (idea.created_by || 'Unknown')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Score</span>
                    <span className="font-semibold text-slate-900">
                      {idea.score ? `⭐ ${idea.score}/5` : 'Not Scored'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Category</span>
                    <span className="font-medium text-slate-800">{idea.category}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Estimated Budget</span>
                    <span className="font-semibold text-slate-900">
                      {formatBudget(idea.estimated_budget)}
                    </span>
                  </div>
                  {isExpanded && (
                    <>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-slate-500">Previous Feedback</span>
                      </div>
                      <div className="mb-2 rounded-lg bg-blue-50 p-3 text-sm italic text-blue-800">
                        {idea.evaluator_comment || 'No previous feedback yet'}
                      </div>
                      {attachmentUrls.length > 0 && (
                        <div className="space-y-2" onClick={(event) => event.stopPropagation()}>
                          <p className="text-slate-500">Attachments</p>
                          <div className="flex flex-wrap gap-2">
                            {attachmentUrls.map((attachmentUrl, index) => {
                              const attachmentHref = resolveAttachmentUrl(attachmentUrl)
                              const imagePreview = isImageAttachment(attachmentUrl)
                              return (
                                <div key={`${idea.id}-file-${index}`} className="flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-2 py-1.5">
                                  {imagePreview && attachmentHref && (
                                    <img
                                      src={attachmentHref}
                                      alt={`Attachment ${index + 1}`}
                                      className="h-8 w-8 rounded object-cover"
                                      loading="lazy"
                                    />
                                  )}
                                  {attachmentHref && (
                                    <a
                                      href={attachmentHref}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="inline-flex w-fit rounded-md border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 transition hover:bg-blue-100"
                                    >
                                      View {index + 1}
                                    </a>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>

                {canManageStatus && isExpanded && (
                  <div className="mt-4 border-t border-slate-100 pt-3" onClick={(event) => event.stopPropagation()}>
                    <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Score (1-5)
                    </label>
                    <select
                      value={scoreInputs[idea.id] ?? ''}
                      onChange={(event) => onScoreChange(idea.id, event.target.value)}
                      className="mb-3 w-full rounded-md border p-2 text-sm focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Not Scored</option>
                      <option value="1">1 - Poor</option>
                      <option value="2">2 - Fair</option>
                      <option value="3">3 - Good</option>
                      <option value="4">4 - Very Good</option>
                      <option value="5">5 - Excellent</option>
                    </select>
                    <textarea
                      value={commentInputs[idea.id] ?? ''}
                      onChange={(event) => onCommentChange(idea.id, event.target.value)}
                      placeholder="Write your evaluation comment here..."
                      rows={3}
                      className="mb-3 w-full rounded-md border p-2 focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Change Status</p>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                      {statusActionButtons.map((action) => (
                        <button
                          key={`${idea.id}-${action.value}`}
                          type="button"
                          className={`rounded-md px-2 py-2 text-xs font-medium text-white transition ${action.className} disabled:cursor-not-allowed disabled:opacity-50`}
                          onClick={() => onUpdateStatus(idea.id, action.value)}
                          disabled={isUpdating}
                        >
                          {isUpdating ? 'Updating...' : action.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {isDraft && isOwner && isExpanded && (
                  <div className="mt-4 border-t border-slate-100 pt-3" onClick={(event) => event.stopPropagation()}>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Draft Actions</p>
                    <button
                      type="button"
                      disabled={isUpdating}
                      className="w-full rounded-md bg-blue-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                      onClick={() => onUpdateStatus(idea.id, 'submitted')}
                    >
                      {isUpdating ? 'Publishing...' : 'Publish Idea'}
                    </button>
                  </div>
                )}
              </article>
            )
          })}
        </section>
      )}
    </>
  )
}

function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const [ideas, setIdeas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedCards, setExpandedCards] = useState(new Set())
  const [updatingIdeaId, setUpdatingIdeaId] = useState('')
  const [commentInputs, setCommentInputs] = useState({})
  const [scoreInputs, setScoreInputs] = useState({})
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userLabel, setUserLabel] = useState('User')
  const [userRole, setUserRole] = useState(null)
  const [userEmail, setUserEmail] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedRole = localStorage.getItem('user_role')
    const storedEmail = localStorage.getItem('user_email')
    const parsedAuth = parseAuthFromToken(token)

    setIsLoggedIn(Boolean(token))
    setUserLabel(storedEmail ? storedEmail.split('@')[0] : parsedAuth.label)
    setUserRole(storedRole || parsedAuth.role)
    setUserEmail(storedEmail || null)
  }, [location.pathname])

  useEffect(() => {
    if (location.pathname !== '/') {
      return
    }

    const loadIdeas = async () => {
      try {
        setLoading(true)
        setError('')
        const data = await fetchIdeas()
        setIdeas(Array.isArray(data) ? data : [])
      } catch (err) {
        setError('Could not load ideas. Please check backend availability.')
      } finally {
        setLoading(false)
      }
    }

    loadIdeas()
  }, [location.pathname])

  const summary = useMemo(() => {
    return ideas.reduce(
      (acc, idea) => {
        const priority = (idea.priority || 'MEDIUM').toUpperCase()
        if (priority === 'HIGH') acc.high += 1
        if (priority === 'MEDIUM') acc.medium += 1
        if (priority === 'LOW') acc.low += 1
        return acc
      },
      { high: 0, medium: 0, low: 0 }
    )
  }, [ideas])

  const toggleCard = (ideaId) => {
    setExpandedCards((prev) => {
      const next = new Set(prev)
      if (next.has(ideaId)) {
        next.delete(ideaId)
      } else {
        next.add(ideaId)
      }
      return next
    })
  }

  const handleStatusUpdate = async (ideaId, status, scoreOverride = undefined) => {
    const evaluatorComment = (commentInputs[ideaId] ?? '').trim()
    const selectedScore = scoreOverride === undefined
      ? scoreInputs[ideaId]
      : scoreOverride
    const score = selectedScore === '' || selectedScore === null || selectedScore === undefined
      ? null
      : Number(selectedScore)

    try {
      setUpdatingIdeaId(ideaId)
      await patchIdeaStatus(ideaId, { status, evaluator_comment: evaluatorComment, score })
      setIdeas((prev) =>
        prev.map((idea) =>
          idea.id === ideaId
            ? { ...idea, status, evaluator_comment: evaluatorComment, score: score ?? idea.score ?? null }
            : idea
        )
      )
      setCommentInputs((prev) => ({ ...prev, [ideaId]: '' }))
    } catch (updateError) {
      setError('Status update failed. Please verify backend PATCH endpoint is running.')
    } finally {
      setUpdatingIdeaId('')
    }
  }

  const handleCommentChange = (ideaId, value) => {
    setCommentInputs((prev) => ({ ...prev, [ideaId]: value }))
  }

  const handleScoreChange = (ideaId, value) => {
    setScoreInputs((prev) => ({ ...prev, [ideaId]: value }))
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_email')
    setIsLoggedIn(false)
    setUserLabel('User')
    setUserRole(null)
    setUserEmail(null)
    navigate('/')
  }

  const canManageStatus = isLoggedIn && ['admin', 'evaluator'].includes(userRole)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-slate-900 text-center text-lg font-bold leading-10 text-white">
              I
            </div>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                Unified Platform
              </p>
              <h1 className="text-xl font-bold text-slate-900">InnovatEPAM Dashboard</h1>
            </div>
          </div>
          <nav className="pointer-events-auto relative z-50 flex items-center gap-2">
            {isLoggedIn && (
              <Link
                to="/submit-idea"
                className="relative z-50 cursor-pointer rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
              >
                Submit New Idea
              </Link>
            )}
            {isLoggedIn ? (
              <div className="flex items-center gap-2">
                <div className="inline-flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700">
                  <span aria-hidden="true">👤</span>
                  <span className="max-w-[180px] truncate">Welcome, {userLabel}</span>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="relative z-50 cursor-pointer rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700"
                >
                  Logout
                </button>
              </div>
            ) : (
              <>
                <Link
                  to="/login"
                  className="relative z-50 cursor-pointer rounded-lg border border-blue-300 px-4 py-2 text-sm font-medium text-blue-600 transition hover:border-blue-500 hover:bg-blue-50 hover:text-blue-800"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="relative z-50 cursor-pointer rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
                >
                  Register
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl px-6 py-8">
        <Routes>
          <Route
            path="/"
            element={
              <DashboardContent
                ideas={ideas}
                loading={loading}
                error={error}
                summary={summary}
                expandedCards={expandedCards}
                onToggleCard={toggleCard}
                onUpdateStatus={handleStatusUpdate}
                updatingIdeaId={updatingIdeaId}
                canManageStatus={canManageStatus}
                commentInputs={commentInputs}
                onCommentChange={handleCommentChange}
                scoreInputs={scoreInputs}
                onScoreChange={handleScoreChange}
                userEmail={userEmail}
                isLoggedIn={isLoggedIn}
                userRole={userRole}
              />
            }
          />
          <Route
            path="/login"
            element={<Login />}
          />
          <Route
            path="/register"
            element={<Register />}
          />
          <Route
            path="/submit-idea"
            element={<SubmitIdea />}
          />
        </Routes>
      </main>
    </div>
  )
}

export default App