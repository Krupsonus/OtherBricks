import { useEffect, useState } from 'react'
import { getCategories, getProducts } from '../api/products'
import ProductCard from '../components/ProductCard'

const LIMIT = 20

const EMPTY_FILTERS = {
  search: '',
  manufacturer: '',
  category_id: '',
  min_price: '',
  max_price: '',
  min_pieces: '',
  max_pieces: '',
  min_age: '',
}

/** Build query params, omitting empty/falsy values. */
function buildParams(filters, offset) {
  const params = { limit: LIMIT, offset }
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== '' && v !== null && v !== undefined) params[k] = v
  })
  return params
}

export default function CatalogPage() {
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [applied, setApplied] = useState(EMPTY_FILTERS)
  const [offset, setOffset] = useState(0)
  const [products, setProducts] = useState([])
  const [total, setTotal] = useState(0)
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getCategories().then((r) => setCategories(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError('')
    getProducts(buildParams(applied, offset))
      .then((r) => {
        setProducts(r.data.items)
        setTotal(r.data.total)
      })
      .catch(() => setError('Failed to load products. Please try again.'))
      .finally(() => setLoading(false))
  }, [applied, offset])

  const handleChange = (e) => {
    setFilters((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleApply = (e) => {
    e.preventDefault()
    setOffset(0)
    setApplied(filters)
  }

  const handleReset = () => {
    setFilters(EMPTY_FILTERS)
    setOffset(0)
    setApplied(EMPTY_FILTERS)
  }

  const totalPages = Math.ceil(total / LIMIT)
  const currentPage = Math.floor(offset / LIMIT) + 1

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Product Catalogue</h1>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filter sidebar */}
        <aside className="lg:w-64 flex-shrink-0" aria-label="Product filters">
          <form onSubmit={handleApply} className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
            <h2 className="font-semibold text-gray-700">Filters</h2>

            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-600 mb-1">Search</label>
              <input id="search" name="search" type="text" value={filters.search} onChange={handleChange}
                placeholder="Product name…"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label htmlFor="manufacturer" className="block text-sm font-medium text-gray-600 mb-1">Manufacturer</label>
              <input id="manufacturer" name="manufacturer" type="text" value={filters.manufacturer} onChange={handleChange}
                placeholder="e.g. Cobi"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label htmlFor="category_id" className="block text-sm font-medium text-gray-600 mb-1">Category</label>
              <select id="category_id" name="category_id" value={filters.category_id} onChange={handleChange}
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">All categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>

            <fieldset className="space-y-2">
              <legend className="text-sm font-medium text-gray-600">Price ($)</legend>
              <div className="flex gap-2">
                <div className="flex-1">
                  <label htmlFor="min_price" className="sr-only">Min price</label>
                  <input id="min_price" name="min_price" type="number" min="0" step="0.01"
                    value={filters.min_price} onChange={handleChange} placeholder="Min"
                    className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div className="flex-1">
                  <label htmlFor="max_price" className="sr-only">Max price</label>
                  <input id="max_price" name="max_price" type="number" min="0" step="0.01"
                    value={filters.max_price} onChange={handleChange} placeholder="Max"
                    className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
            </fieldset>

            <fieldset className="space-y-2">
              <legend className="text-sm font-medium text-gray-600">Piece count</legend>
              <div className="flex gap-2">
                <div className="flex-1">
                  <label htmlFor="min_pieces" className="sr-only">Min pieces</label>
                  <input id="min_pieces" name="min_pieces" type="number" min="1"
                    value={filters.min_pieces} onChange={handleChange} placeholder="Min"
                    className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div className="flex-1">
                  <label htmlFor="max_pieces" className="sr-only">Max pieces</label>
                  <input id="max_pieces" name="max_pieces" type="number" min="1"
                    value={filters.max_pieces} onChange={handleChange} placeholder="Max"
                    className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
            </fieldset>

            <div>
              <label htmlFor="min_age" className="block text-sm font-medium text-gray-600 mb-1">Min age</label>
              <input id="min_age" name="min_age" type="number" min="0"
                value={filters.min_age} onChange={handleChange} placeholder="e.g. 8"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div className="flex gap-2 pt-2">
              <button type="submit"
                className="flex-1 bg-indigo-600 text-white text-sm py-1.5 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                Apply
              </button>
              <button type="button" onClick={handleReset}
                className="flex-1 border border-gray-300 text-sm py-1.5 rounded hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                Reset
              </button>
            </div>
          </form>
        </aside>

        {/* Product grid */}
        <section className="flex-1" aria-label="Product list" aria-live="polite">
          {error && (
            <div role="alert" className="mb-4 rounded bg-red-50 border border-red-300 text-red-700 px-4 py-3 text-sm">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-500">
              {loading ? 'Loading…' : `${total} product${total !== 1 ? 's' : ''} found`}
            </p>
          </div>

          {!loading && products.length === 0 && !error && (
            <p className="text-gray-500 text-sm py-12 text-center">No products match your filters.</p>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <nav className="mt-8 flex items-center justify-center gap-3" aria-label="Pagination">
              <button
                onClick={() => setOffset((o) => Math.max(0, o - LIMIT))}
                disabled={offset === 0}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                aria-label="Previous page"
              >
                ← Previous
              </button>
              <span className="text-sm text-gray-600">Page {currentPage} of {totalPages}</span>
              <button
                onClick={() => setOffset((o) => o + LIMIT)}
                disabled={offset + LIMIT >= total}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                aria-label="Next page"
              >
                Next →
              </button>
            </nav>
          )}
        </section>
      </div>
    </main>
  )
}
