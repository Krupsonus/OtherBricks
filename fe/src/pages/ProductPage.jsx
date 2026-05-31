import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getProduct, getPriceOffers } from '../api/products'
import { addToWishlist, createWishlist, getWishlists, removeFromWishlist } from '../api/wishlists'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

/** Full product detail page with external price comparison. */
export default function ProductPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const { addToCart } = useCart()
  const [product, setProduct] = useState(null)
  const [added, setAdded] = useState(false)
  const [offers, setOffers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Wishlist picker state
  const [showPicker, setShowPicker] = useState(false)
  const [wishlists, setWishlists] = useState([])
  const [newListName, setNewListName] = useState('')
  const [pickerMsg, setPickerMsg] = useState('')
  const pickerRef = useRef(null)

  // Close picker when clicking outside
  useEffect(() => {
    if (!showPicker) return
    const handler = (e) => {
      if (pickerRef.current && !pickerRef.current.contains(e.target)) {
        setShowPicker(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [showPicker])

  const openPicker = () => {
    setPickerMsg('')
    setNewListName('')
    setShowPicker(true)
  }

  const handleToggleList = async (wl) => {
    const productId = Number(id)
    const alreadySaved = wl.products.some((p) => p.id === productId)
    try {
      const res = alreadySaved
        ? await removeFromWishlist(wl.id, id)
        : await addToWishlist(wl.id, id)
      setWishlists((prev) => prev.map((w) => (w.id === wl.id ? res.data : w)))
      setPickerMsg(alreadySaved ? `Removed from "${wl.name}"` : `Added to "${wl.name}"!`)
      setTimeout(() => setPickerMsg(''), 2000)
    } catch {
      setPickerMsg('Could not update wishlist.')
    }
  }

  const handleCreateAndAdd = async (e) => {
    e.preventDefault()
    const name = newListName.trim()
    if (!name) return
    try {
      const listRes = await createWishlist(name)
      const newList = listRes.data
      const addRes = await addToWishlist(newList.id, id)
      setWishlists((prev) => [addRes.data, ...prev])
      setNewListName('')
      setPickerMsg(`Added to "${newList.name}"!`)
      setTimeout(() => setPickerMsg(''), 2000)
    } catch {
      setPickerMsg('Could not create wishlist.')
    }
  }

  useEffect(() => {
    setLoading(true)
    const calls = [getProduct(id), getPriceOffers(id)]
    if (user) calls.push(getWishlists())
    Promise.all(calls)
      .then(([productRes, offersRes, wishlistsRes]) => {
        setProduct(productRes.data)
        setOffers(offersRes.data)
        if (wishlistsRes) setWishlists(wishlistsRes.data)
      })
      .catch((err) => {
        setError(err.response?.status === 404 ? 'Product not found.' : 'Failed to load product.')
      })
      .finally(() => setLoading(false))
  }, [id, user])

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-500">Loading…</p>
      </main>
    )
  }

  if (error) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <Link to="/products" className="text-indigo-600 hover:underline">← Back to catalogue</Link>
      </main>
    )
  }

  const { name, manufacturer, description, piece_count, min_age, base_price, stock_quantity, image_url, category } = product

  const cheapest = offers.length > 0 ? offers[0] : null
  const productId = Number(id)
  const isSaved = wishlists.some((wl) => wl.products.some((p) => p.id === productId))

  const handleAddToCart = () => {
    addToCart(product)
    setAdded(true)
    setTimeout(() => setAdded(false), 2000)
  }

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link to="/products" className="inline-flex items-center text-sm text-indigo-600 hover:underline mb-6 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded">
        ← Back to catalogue
      </Link>

      <article className="bg-white rounded-lg border border-gray-200 p-6 flex flex-col md:flex-row gap-8">
        {/* Image */}
        <div className="md:w-64 flex-shrink-0">
          <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
            {image_url ? (
              <img src={image_url} alt={name} className="object-cover w-full h-full" />
            ) : (
              <span className="text-gray-400 text-sm" aria-hidden="true">No image</span>
            )}
          </div>
        </div>

        {/* Details */}
        <div className="flex-1">
          {category && (
            <span className="text-xs font-medium text-indigo-600 uppercase tracking-wide">{category.name}</span>
          )}
          <h1 className="text-2xl font-bold text-gray-800 mt-1 mb-1">{name}</h1>
          <p className="text-gray-500 text-sm mb-4">{manufacturer}</p>

          {description && (
            <p className="text-gray-600 text-sm mb-6">{description}</p>
          )}

          <div className="mb-4 flex flex-wrap gap-2 items-center">
            <button
              onClick={handleAddToCart}
              disabled={stock_quantity === 0}
              className="w-full sm:w-auto bg-indigo-600 text-white text-sm px-6 py-2.5 rounded hover:bg-indigo-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
              aria-live="polite"
            >
              {added ? '✓ Added to cart' : stock_quantity === 0 ? 'Out of stock' : 'Add to cart'}
            </button>

            {user && (
              <div className="relative" ref={pickerRef}>
                <button
                  onClick={openPicker}
                  className={`w-full sm:w-auto text-sm px-4 py-2.5 rounded border focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors ${
                    isSaved
                      ? 'bg-indigo-50 border-indigo-400 text-indigo-700 font-medium'
                      : 'border-gray-300 text-gray-700 hover:border-indigo-400 hover:text-indigo-600'
                  }`}
                  aria-expanded={showPicker}
                  aria-haspopup="listbox"
                  aria-pressed={isSaved}
                >
                  {isSaved ? '♥ Saved to wishlist' : '♡ Save to wishlist'}
                </button>

                {showPicker && (
                  <div
                    className="absolute left-0 top-full mt-1 z-10 w-64 bg-white rounded-lg border border-gray-200 shadow-lg"
                    role="dialog"
                    aria-label="Choose wishlist"
                  >
                    <div className="p-3 border-b border-gray-100">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Save to wishlist</p>
                    </div>

                    {pickerMsg && (
                      <p className="px-3 py-2 text-xs text-indigo-600 font-medium" role="status">{pickerMsg}</p>
                    )}

                    {wishlists.length > 0 && (
                      <ul role="listbox" className="max-h-40 overflow-y-auto divide-y divide-gray-50">
                        {wishlists.map((wl) => {
                          const inList = wl.products.some((p) => p.id === productId)
                          return (
                            <li key={wl.id}>
                              <button
                                onClick={() => handleToggleList(wl)}
                                className={`w-full text-left px-3 py-2 text-sm flex items-center justify-between gap-2 focus:outline-none focus:bg-indigo-50 ${
                                  inList
                                    ? 'text-indigo-700 bg-indigo-50 hover:bg-indigo-100'
                                    : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'
                                }`}
                                role="option"
                                aria-selected={inList}
                              >
                                <span className="truncate">{wl.name}</span>
                                <span className="flex-shrink-0 text-xs text-gray-400">
                                  {inList ? '✓' : `${wl.products.length}`}
                                </span>
                              </button>
                            </li>
                          )
                        })}
                      </ul>
                    )}

                    <form onSubmit={handleCreateAndAdd} className="p-3 border-t border-gray-100">
                      <p className="text-xs text-gray-500 mb-1">New list</p>
                      <div className="flex gap-1">
                        <input
                          type="text"
                          value={newListName}
                          onChange={(e) => setNewListName(e.target.value)}
                          placeholder="List name…"
                          maxLength={100}
                          className="flex-1 border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          aria-label="New wishlist name"
                        />
                        <button
                          type="submit"
                          disabled={!newListName.trim()}
                          className="bg-indigo-600 text-white text-xs px-2 py-1 rounded hover:bg-indigo-700 disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                          Add
                        </button>
                      </div>
                    </form>
                  </div>
                )}
              </div>
            )}
          </div>

          <dl className="grid grid-cols-2 gap-3 text-sm mb-6">
            <div className="bg-gray-50 rounded p-3">
              <dt className="text-gray-500 text-xs mb-0.5">Piece count</dt>
              <dd className="font-semibold text-gray-800">{piece_count}</dd>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <dt className="text-gray-500 text-xs mb-0.5">Minimum age</dt>
              <dd className="font-semibold text-gray-800">{min_age ? `${min_age}+` : '—'}</dd>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <dt className="text-gray-500 text-xs mb-0.5">Our price</dt>
              <dd className="font-semibold text-gray-800 text-lg">${Number(base_price).toFixed(2)}</dd>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <dt className="text-gray-500 text-xs mb-0.5">Availability</dt>
              <dd className={`font-semibold ${stock_quantity > 0 ? 'text-green-600' : 'text-red-500'}`}>
                {stock_quantity > 0 ? `In stock (${stock_quantity})` : 'Out of stock'}
              </dd>
            </div>
          </dl>
        </div>
      </article>

      {/* Price comparison */}
      <section className="mt-6" aria-label="Price comparison">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Compare prices</h2>

        {offers.length === 0 ? (
          <p className="text-sm text-gray-500 py-6 text-center bg-white rounded-lg border border-gray-200">
            No external price offers available for this product.
          </p>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
            {offers.map((offer, idx) => (
              <div
                key={offer.id}
                className="flex items-center justify-between px-4 py-3 gap-4"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {idx === 0 && (
                    <span className="flex-shrink-0 text-xs font-medium bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                      Best price
                    </span>
                  )}
                  <span className="text-sm font-medium text-gray-800 truncate">{offer.shop_name}</span>
                </div>

                <div className="flex items-center gap-4 flex-shrink-0">
                  <span className={`text-lg font-bold ${idx === 0 ? 'text-green-700' : 'text-gray-800'}`}>
                    ${Number(offer.price).toFixed(2)}
                  </span>
                  <a
                    href={offer.shop_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm bg-indigo-600 text-white px-3 py-1.5 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    aria-label={`Buy at ${offer.shop_name} for $${Number(offer.price).toFixed(2)}`}
                  >
                    Buy
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        {cheapest && (
          <p className="mt-2 text-xs text-gray-400 text-right">
            Prices updated: {new Date(cheapest.updated_at).toLocaleDateString()}
          </p>
        )}
      </section>
    </main>
  )
}
