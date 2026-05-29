import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { placeOrder } from '../api/orders'

export default function CartPage() {
  const { user } = useAuth()
  const { items, updateQuantity, removeFromCart, clearCart, totalPrice } = useCart()
  const navigate = useNavigate()

  const [address, setAddress] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [confirmedOrder, setConfirmedOrder] = useState(null)

  if (confirmedOrder) {
    return (
      <main className="max-w-lg mx-auto px-4 py-16 text-center">
        <div className="bg-green-50 border border-green-200 rounded-lg p-8">
          <p className="text-4xl mb-4" aria-hidden="true">✓</p>
          <h1 className="text-2xl font-bold text-green-800 mb-2">Order placed!</h1>
          <p className="text-green-700 mb-1">Order #{confirmedOrder.id}</p>
          <p className="text-green-600 text-sm mb-6">
            Total: <span className="font-semibold">${Number(confirmedOrder.total_amount).toFixed(2)}</span>
          </p>
          <div className="flex gap-3 justify-center">
            <Link
              to="/products"
              className="text-sm bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Continue shopping
            </Link>
            <Link
              to="/orders"
              className="text-sm border border-gray-300 px-4 py-2 rounded hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              My orders
            </Link>
          </div>
        </div>
      </main>
    )
  }

  if (items.length === 0) {
    return (
      <main className="max-w-lg mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Your cart is empty</h1>
        <Link to="/products" className="text-indigo-600 hover:underline">Browse the catalogue →</Link>
      </main>
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!user) {
      navigate('/login')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const { data } = await placeOrder({
        items: items.map((i) => ({ product_id: i.id, quantity: i.quantity })),
        shipping_address: address,
        payment_method: 'stripe',
      })
      clearCart()
      setConfirmedOrder(data)
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Failed to place order. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Your cart</h1>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Item list */}
        <section className="flex-1" aria-label="Cart items">
          <ul className="space-y-3">
            {items.map((item) => (
              <li
                key={item.id}
                className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4"
              >
                <div className="w-14 h-14 bg-gray-100 rounded flex-shrink-0 overflow-hidden">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.name} className="w-full h-full object-cover" />
                  ) : (
                    <span className="w-full h-full flex items-center justify-center text-gray-400 text-xs" aria-hidden="true">—</span>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{item.name}</p>
                  <p className="text-sm text-gray-500">${item.price.toFixed(2)} each</p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    className="w-7 h-7 rounded border border-gray-300 text-gray-600 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex items-center justify-center"
                    aria-label={`Decrease quantity of ${item.name}`}
                  >
                    −
                  </button>
                  <span className="w-6 text-center text-sm font-medium" aria-label="Quantity">
                    {item.quantity}
                  </span>
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    className="w-7 h-7 rounded border border-gray-300 text-gray-600 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex items-center justify-center"
                    aria-label={`Increase quantity of ${item.name}`}
                  >
                    +
                  </button>
                </div>

                <p className="text-sm font-semibold text-gray-800 w-20 text-right">
                  ${(item.price * item.quantity).toFixed(2)}
                </p>

                <button
                  onClick={() => removeFromCart(item.id)}
                  className="text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                  aria-label={`Remove ${item.name} from cart`}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </section>

        {/* Order summary + checkout */}
        <aside className="lg:w-80 flex-shrink-0">
          <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            <h2 className="font-semibold text-gray-800">Order summary</h2>

            <div className="flex justify-between text-sm text-gray-600">
              <span>Subtotal</span>
              <span className="font-medium">${totalPrice.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Shipping</span>
              <span className="text-green-600 font-medium">Free</span>
            </div>
            <div className="border-t pt-3 flex justify-between font-semibold text-gray-800">
              <span>Total</span>
              <span>${totalPrice.toFixed(2)}</span>
            </div>

            {user ? (
              <form onSubmit={handleSubmit} className="space-y-3 pt-2">
                <div>
                  <label htmlFor="address" className="block text-sm font-medium text-gray-600 mb-1">
                    Shipping address
                  </label>
                  <textarea
                    id="address"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    required
                    minLength={5}
                    rows={3}
                    placeholder="Street, city, postcode"
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                  />
                </div>

                {error && (
                  <p role="alert" className="text-sm text-red-600">{error}</p>
                )}

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full bg-indigo-600 text-white text-sm py-2.5 rounded hover:bg-indigo-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {submitting ? 'Placing order…' : 'Place order'}
                </button>
              </form>
            ) : (
              <div className="pt-2 space-y-2">
                <p className="text-sm text-gray-500">Sign in to complete your purchase.</p>
                <Link
                  to="/login"
                  className="block w-full text-center bg-indigo-600 text-white text-sm py-2.5 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  Log in to checkout
                </Link>
              </div>
            )}
          </div>
        </aside>
      </div>
    </main>
  )
}
