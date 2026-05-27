import { Link } from 'react-router-dom'

/** Card displayed in the product grid on the catalogue page. */
export default function ProductCard({ product }) {
  const { id, name, manufacturer, piece_count, min_age, base_price, stock_quantity, image_url, category } = product

  return (
    <article className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col hover:shadow-md transition-shadow">
      <div className="aspect-square bg-gray-100 rounded-t-lg flex items-center justify-center overflow-hidden">
        {image_url ? (
          <img src={image_url} alt={name} className="object-cover w-full h-full" />
        ) : (
          <span className="text-gray-400 text-sm" aria-hidden="true">No image</span>
        )}
      </div>

      <div className="p-4 flex flex-col flex-1">
        {category && (
          <span className="text-xs font-medium text-indigo-600 uppercase tracking-wide mb-1">
            {category.name}
          </span>
        )}

        <h2 className="text-sm font-semibold text-gray-800 mb-1 line-clamp-2">{name}</h2>
        <p className="text-xs text-gray-500 mb-3">{manufacturer}</p>

        <dl className="flex gap-3 text-xs text-gray-500 mb-4">
          <div>
            <dt className="sr-only">Piece count</dt>
            <dd>{piece_count} pcs</dd>
          </div>
          {min_age && (
            <div>
              <dt className="sr-only">Minimum age</dt>
              <dd>Age {min_age}+</dd>
            </div>
          )}
        </dl>

        <div className="mt-auto flex items-center justify-between">
          <span className="text-lg font-bold text-gray-900">${Number(base_price).toFixed(2)}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${stock_quantity > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
            {stock_quantity > 0 ? 'In stock' : 'Out of stock'}
          </span>
        </div>

        <Link
          to={`/products/${id}`}
          className="mt-3 block text-center text-sm bg-indigo-600 text-white py-1.5 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          View details
        </Link>
      </div>
    </article>
  )
}
