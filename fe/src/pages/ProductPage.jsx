import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getProduct } from '../api/products'

/** Full product detail page. */
export default function ProductPage() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    getProduct(id)
      .then((r) => setProduct(r.data))
      .catch((err) => {
        setError(err.response?.status === 404 ? 'Product not found.' : 'Failed to load product.')
      })
      .finally(() => setLoading(false))
  }, [id])

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
              <dt className="text-gray-500 text-xs mb-0.5">Price</dt>
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
    </main>
  )
}
