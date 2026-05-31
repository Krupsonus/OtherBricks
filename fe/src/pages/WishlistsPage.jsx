import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  createWishlist,
  deleteWishlist,
  getWishlists,
  removeFromWishlist,
} from '../api/wishlists'

export default function WishlistsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [wishlists, setWishlists] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [newName, setNewName] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }
    getWishlists()
      .then((res) => setWishlists(res.data))
      .catch(() => setError('Failed to load wishlists.'))
      .finally(() => setLoading(false))
  }, [user, navigate])

  const handleCreate = async (e) => {
    e.preventDefault()
    const name = newName.trim()
    if (!name) return
    setCreating(true)
    setCreateError('')
    try {
      const res = await createWishlist(name)
      setWishlists((prev) => [res.data, ...prev])
      setNewName('')
    } catch {
      setCreateError('Could not create wishlist.')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await deleteWishlist(id)
      setWishlists((prev) => prev.filter((wl) => wl.id !== id))
    } catch {
      setError('Could not delete wishlist.')
    }
  }

  const handleRemoveProduct = async (wishlistId, productId) => {
    try {
      const res = await removeFromWishlist(wishlistId, productId)
      setWishlists((prev) =>
        prev.map((wl) => (wl.id === wishlistId ? res.data : wl))
      )
    } catch {
      setError('Could not remove product.')
    }
  }

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-500">Loading…</p>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My wishlists</h1>

      {error && (
        <p className="text-red-600 mb-4 text-sm" role="alert">{error}</p>
      )}

      {/* Create new wishlist */}
      <form
        onSubmit={handleCreate}
        className="flex gap-2 mb-8"
        aria-label="Create new wishlist"
      >
        <input
          ref={inputRef}
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="New wishlist name…"
          maxLength={100}
          className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          aria-label="Wishlist name"
        />
        <button
          type="submit"
          disabled={creating || !newName.trim()}
          className="bg-indigo-600 text-white text-sm px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {creating ? 'Creating…' : 'Create'}
        </button>
      </form>
      {createError && (
        <p className="text-red-600 text-sm -mt-6 mb-4" role="alert">{createError}</p>
      )}

      {/* Wishlist cards */}
      {wishlists.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 py-16 text-center">
          <p className="text-gray-500 text-sm mb-2">You have no wishlists yet.</p>
          <p className="text-gray-400 text-xs">
            Create one above, then add products from any{' '}
            <Link to="/products" className="text-indigo-600 hover:underline">
              product page
            </Link>
            .
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {wishlists.map((wl) => (
            <section
              key={wl.id}
              className="bg-white rounded-lg border border-gray-200"
              aria-label={`Wishlist: ${wl.name}`}
            >
              {/* Wishlist header */}
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                <div>
                  <h2 className="font-semibold text-gray-800">{wl.name}</h2>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {wl.products.length} product{wl.products.length !== 1 ? 's' : ''}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(wl.id)}
                  className="text-xs text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 rounded px-2 py-1"
                  aria-label={`Delete wishlist ${wl.name}`}
                >
                  Delete list
                </button>
              </div>

              {/* Products grid */}
              {wl.products.length === 0 ? (
                <p className="text-sm text-gray-400 px-5 py-6 text-center">
                  No products in this list yet.
                </p>
              ) : (
                <ul className="divide-y divide-gray-50" role="list">
                  {wl.products.map((product) => (
                    <li
                      key={product.id}
                      className="flex items-center gap-4 px-5 py-3"
                    >
                      {/* Thumbnail */}
                      <div className="w-12 h-12 flex-shrink-0 bg-gray-100 rounded overflow-hidden">
                        {product.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <span className="flex items-center justify-center w-full h-full text-gray-300 text-xs" aria-hidden="true">
                            ◻
                          </span>
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <Link
                          to={`/products/${product.id}`}
                          className="text-sm font-medium text-gray-800 hover:text-indigo-600 truncate block focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
                        >
                          {product.name}
                        </Link>
                        <p className="text-xs text-gray-500">{product.manufacturer}</p>
                      </div>

                      {/* Price */}
                      <span className="text-sm font-semibold text-gray-800 flex-shrink-0">
                        ${Number(product.base_price).toFixed(2)}
                      </span>

                      {/* Remove */}
                      <button
                        onClick={() => handleRemoveProduct(wl.id, product.id)}
                        className="text-xs text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-red-400 rounded px-1"
                        aria-label={`Remove ${product.name} from ${wl.name}`}
                      >
                        ✕
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          ))}
        </div>
      )}
    </main>
  )
}
