import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { updateProfile } from '../api/users'

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user) {
    navigate('/login')
    return null
  }

  const [form, setForm] = useState({
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    password: '',
  })
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
    setSuccess(false)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setSaving(true)

    const payload = {}
    if (form.first_name !== user.first_name) payload.first_name = form.first_name
    if (form.last_name !== user.last_name) payload.last_name = form.last_name
    if (form.email !== user.email) payload.email = form.email
    if (form.password.trim()) payload.password = form.password.trim()

    if (Object.keys(payload).length === 0) {
      setSaving(false)
      setSuccess(true)
      return
    }

    try {
      await updateProfile(payload)
      setSuccess(true)
      setForm((f) => ({ ...f, password: '' }))
      if (payload.email) {
        logout()
        navigate('/login')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save changes.')
    } finally {
      setSaving(false)
    }
  }

  const fieldCls = 'w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'

  return (
    <main className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My profile</h1>

      <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">First name</label>
            <input
              type="text"
              name="first_name"
              value={form.first_name}
              onChange={handleChange}
              required
              className={fieldCls}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Last name</label>
            <input
              type="text"
              name="last_name"
              value={form.last_name}
              onChange={handleChange}
              required
              className={fieldCls}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
            className={fieldCls}
          />
          {form.email !== user.email && (
            <p className="text-xs text-amber-600 mt-1">Changing your email will log you out.</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">New password</label>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Leave blank to keep current"
            minLength={8}
            className={fieldCls}
          />
        </div>

        {error && <p className="text-red-600 text-sm" role="alert">{error}</p>}
        {success && <p className="text-green-600 text-sm">Changes saved.</p>}

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-indigo-600 text-white py-2 rounded text-sm font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Save changes'}
        </button>
      </form>
    </main>
  )
}
