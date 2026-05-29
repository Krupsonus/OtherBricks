import { createContext, useContext, useEffect, useState } from 'react'

const CartContext = createContext(null)

const STORAGE_KEY = 'ob_cart'

function loadCart() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

/** Cart item shape: { id, name, price, image_url, quantity } */
export function CartProvider({ children }) {
  const [items, setItems] = useState(loadCart)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }, [items])

  const addToCart = (product, qty = 1) => {
    setItems((prev) => {
      const existing = prev.find((i) => i.id === product.id)
      if (existing) {
        return prev.map((i) =>
          i.id === product.id ? { ...i, quantity: i.quantity + qty } : i
        )
      }
      return [
        ...prev,
        {
          id: product.id,
          name: product.name,
          price: Number(product.base_price),
          image_url: product.image_url,
          quantity: qty,
        },
      ]
    })
  }

  const updateQuantity = (productId, qty) => {
    if (qty < 1) return removeFromCart(productId)
    setItems((prev) =>
      prev.map((i) => (i.id === productId ? { ...i, quantity: qty } : i))
    )
  }

  const removeFromCart = (productId) => {
    setItems((prev) => prev.filter((i) => i.id !== productId))
  }

  const clearCart = () => setItems([])

  const totalItems = items.reduce((sum, i) => sum + i.quantity, 0)
  const totalPrice = items.reduce((sum, i) => sum + i.price * i.quantity, 0)

  return (
    <CartContext.Provider
      value={{ items, addToCart, updateQuantity, removeFromCart, clearCart, totalItems, totalPrice }}
    >
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  return useContext(CartContext)
}
