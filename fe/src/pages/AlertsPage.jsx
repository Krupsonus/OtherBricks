import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { deleteAlert, getAlerts } from '../api/alerts'
import { useAuth } from '../context/AuthContext'

export default function AlertsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    getAlerts()
      .then((res) => setAlerts(res.data))
      .catch(() => setError('Failed to load alerts.'))
      .finally(() => setLoading(false))
  }, [user, navigate])

  const handleDelete = async (id) => {
    try {
      await deleteAlert(id)
      setAlerts((prev) => prev.filter((a) => a.id !== id))
    } catch {
      setError('Could not delete alert.')
    }
  }

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-500">Loading…</p>
      </main>
    )
  }

  const triggered = alerts.filter((a) => a.is_triggered)
  const pending = alerts.filter((a) => !a.is_triggered)

  return (
    <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">
        Price alerts
        {alerts.length > 0 && (
          <span className="ml-2 text-sm font-normal text-gray-400">({alerts.length})</span>
        )}
      </h1>

      {error && <p className="text-red-600 text-sm mb-4" role="alert">{error}</p>}

      {alerts.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 py-16 text-center">
          <p className="text-gray-500 text-sm mb-2">No price alerts yet.</p>
          <p className="text-gray-400 text-xs">
            Set an alert on any{' '}
            <Link to="/products" className="text-indigo-600 hover:underline">product page</Link>
            {' '}to be notified when the price drops.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {triggered.length > 0 && (
            <p className="text-xs font-semibold text-green-700 uppercase tracking-wide">
              Triggered — price reached your target
            </p>
          )}
          {[...triggered, ...pending].map((alert) => (
            <div
              key={alert.id}
              className={`bg-white rounded-lg border px-5 py-4 flex items-center gap-4 ${
                alert.is_triggered ? 'border-green-300' : 'border-gray-200'
              }`}
            >
              {/* Status badge */}
              <span
                className={`flex-shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${
                  alert.is_triggered
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-500'
                }`}
              >
                {alert.is_triggered ? 'Triggered' : 'Watching'}
              </span>

              {/* Product name */}
              <div className="flex-1 min-w-0">
                <Link
                  to={`/products/${alert.product_id}`}
                  className="text-sm font-medium text-gray-800 hover:text-indigo-600 truncate block focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
                >
                  {alert.product_name}
                </Link>
                <p className="text-xs text-gray-400 mt-0.5">
                  Your target: <span className="font-semibold text-gray-600">${Number(alert.target_price).toFixed(2)}</span>
                  {alert.best_offer_price != null && (
                    <span className="ml-2">
                      · Best now:{' '}
                      <span className={`font-semibold ${alert.is_triggered ? 'text-green-600' : 'text-gray-600'}`}>
                        ${Number(alert.best_offer_price).toFixed(2)}
                      </span>
                    </span>
                  )}
                  {alert.best_offer_price == null && (
                    <span className="ml-2 text-gray-400">· No offers yet</span>
                  )}
                </p>
              </div>

              {/* Delete */}
              <button
                onClick={() => handleDelete(alert.id)}
                className="flex-shrink-0 text-xs text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-red-400 rounded px-1"
                aria-label={`Delete alert for ${alert.product_name}`}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  )
}
