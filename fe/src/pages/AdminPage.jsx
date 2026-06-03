import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  adminCreateProduct,
  adminDeleteProduct,
  adminGetOrders,
  adminGetProducts,
  adminGetUsers,
  adminUpdateProduct,
} from '../api/admin'
import { useAuth } from '../context/AuthContext'

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-700',
  paid: 'bg-blue-100 text-blue-700',
  shipped: 'bg-indigo-100 text-indigo-700',
  delivered: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
}

const EMPTY_FORM = {
  name: '', manufacturer: '', description: '', piece_count: '',
  min_age: '', base_price: '', stock_quantity: '', image_url: '', category_id: '',
}

export default function AdminPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState('products')

  // Products state
  const [products, setProducts] = useState([])
  const [prodLoading, setProdLoading] = useState(false)
  const [prodError, setProdError] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [addForm, setAddForm] = useState(EMPTY_FORM)
  const [addError, setAddError] = useState('')
  const [editId, setEditId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [editError, setEditError] = useState('')

  // Orders state
  const [orders, setOrders] = useState([])
  const [ordLoading, setOrdLoading] = useState(false)

  // Users state
  const [users, setUsers] = useState([])
  const [usrLoading, setUsrLoading] = useState(false)

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    if (user.role !== 'admin') { navigate('/'); return }
  }, [user, navigate])

  useEffect(() => {
    if (!user || user.role !== 'admin') return
    if (tab === 'products' && products.length === 0) loadProducts()
    if (tab === 'orders' && orders.length === 0) loadOrders()
    if (tab === 'users' && users.length === 0) loadUsers()
  }, [tab, user])

  const loadProducts = () => {
    setProdLoading(true)
    adminGetProducts()
      .then((r) => setProducts(r.data))
      .catch(() => setProdError('Failed to load products.'))
      .finally(() => setProdLoading(false))
  }

  const loadOrders = () => {
    setOrdLoading(true)
    adminGetOrders()
      .then((r) => setOrders(r.data))
      .finally(() => setOrdLoading(false))
  }

  const loadUsers = () => {
    setUsrLoading(true)
    adminGetUsers()
      .then((r) => setUsers(r.data))
      .finally(() => setUsrLoading(false))
  }

  // ── Add product ──────────────────────────────────────────────────────────
  const handleAdd = async (e) => {
    e.preventDefault()
    setAddError('')
    const payload = {
      name: addForm.name.trim(),
      manufacturer: addForm.manufacturer.trim(),
      description: addForm.description.trim() || null,
      piece_count: parseInt(addForm.piece_count),
      min_age: addForm.min_age ? parseInt(addForm.min_age) : null,
      base_price: parseFloat(addForm.base_price),
      stock_quantity: parseInt(addForm.stock_quantity) || 0,
      image_url: addForm.image_url.trim() || null,
      category_id: addForm.category_id ? parseInt(addForm.category_id) : null,
    }
    try {
      const res = await adminCreateProduct(payload)
      setProducts((prev) => [res.data, ...prev])
      setAddForm(EMPTY_FORM)
      setShowAddForm(false)
    } catch (err) {
      setAddError(err.response?.data?.detail || 'Could not create product.')
    }
  }

  // ── Edit product ─────────────────────────────────────────────────────────
  const startEdit = (product) => {
    setEditId(product.id)
    setEditForm({
      name: product.name,
      manufacturer: product.manufacturer,
      description: product.description || '',
      piece_count: product.piece_count,
      min_age: product.min_age ?? '',
      base_price: product.base_price,
      stock_quantity: product.stock_quantity,
      image_url: product.image_url || '',
      category_id: product.category_id ?? '',
    })
    setEditError('')
  }

  const handleEdit = async (e) => {
    e.preventDefault()
    setEditError('')
    const payload = {
      name: editForm.name.trim(),
      manufacturer: editForm.manufacturer.trim(),
      description: editForm.description.trim() || null,
      piece_count: parseInt(editForm.piece_count),
      min_age: editForm.min_age !== '' ? parseInt(editForm.min_age) : null,
      base_price: parseFloat(editForm.base_price),
      stock_quantity: parseInt(editForm.stock_quantity),
      image_url: editForm.image_url.trim() || null,
      category_id: editForm.category_id !== '' ? parseInt(editForm.category_id) : null,
    }
    try {
      const res = await adminUpdateProduct(editId, payload)
      setProducts((prev) => prev.map((p) => (p.id === editId ? res.data : p)))
      setEditId(null)
    } catch (err) {
      setEditError(err.response?.data?.detail || 'Could not update product.')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this product?')) return
    try {
      await adminDeleteProduct(id)
      setProducts((prev) => prev.filter((p) => p.id !== id))
    } catch {
      setProdError('Could not delete product.')
    }
  }

  const tabBtn = (key, label) => (
    <button
      key={key}
      onClick={() => setTab(key)}
      className={`px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 focus:outline-none ${
        tab === key
          ? 'border-indigo-600 text-indigo-600'
          : 'border-transparent text-gray-500 hover:text-gray-700'
      }`}
    >
      {label}
    </button>
  )

  const fieldCls = 'border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'

  const ProductForm = ({ form, setForm, onSubmit, submitLabel, error, onCancel }) => (
    <form onSubmit={onSubmit} className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
      <div className="grid grid-cols-2 gap-3 mb-3">
        {[
          ['name', 'Name *', 'text', true],
          ['manufacturer', 'Manufacturer *', 'text', true],
          ['piece_count', 'Piece count *', 'number', true],
          ['base_price', 'Price ($) *', 'number', true],
          ['stock_quantity', 'Stock', 'number', false],
          ['min_age', 'Min age', 'number', false],
          ['category_id', 'Category ID', 'number', false],
          ['image_url', 'Image URL', 'text', false],
        ].map(([key, label, type, required]) => (
          <div key={key}>
            <label className="block text-xs text-gray-500 mb-0.5">{label}</label>
            <input
              type={type}
              value={form[key]}
              onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
              required={required}
              min={type === 'number' ? '0' : undefined}
              step={key === 'base_price' ? '0.01' : undefined}
              className={`w-full ${fieldCls}`}
            />
          </div>
        ))}
      </div>
      <div className="mb-3">
        <label className="block text-xs text-gray-500 mb-0.5">Description</label>
        <textarea
          value={form.description}
          onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          rows={2}
          className={`w-full resize-none ${fieldCls}`}
        />
      </div>
      {error && <p className="text-red-600 text-xs mb-2" role="alert">{error}</p>}
      <div className="flex gap-2">
        <button type="submit" className="bg-indigo-600 text-white text-sm px-4 py-1.5 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
          {submitLabel}
        </button>
        <button type="button" onClick={onCancel} className="text-sm text-gray-500 hover:text-gray-700 px-2">
          Cancel
        </button>
      </div>
    </form>
  )

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Admin panel</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {tabBtn('products', `Products (${products.length})`)}
        {tabBtn('orders', `Orders (${orders.length})`)}
        {tabBtn('users', `Users (${users.length})`)}
      </div>

      {/* ── Products tab ─────────────────────────────────────────────────── */}
      {tab === 'products' && (
        <div>
          {prodError && <p className="text-red-600 text-sm mb-3" role="alert">{prodError}</p>}

          <div className="mb-4">
            {!showAddForm ? (
              <button
                onClick={() => setShowAddForm(true)}
                className="bg-indigo-600 text-white text-sm px-4 py-2 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                + Add product
              </button>
            ) : (
              <ProductForm
                form={addForm}
                setForm={setAddForm}
                onSubmit={handleAdd}
                submitLabel="Create"
                error={addError}
                onCancel={() => { setShowAddForm(false); setAddError('') }}
              />
            )}
          </div>

          {prodLoading ? (
            <p className="text-gray-500 text-sm">Loading…</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs text-gray-500 uppercase tracking-wide">
                    <th className="px-3 py-2 font-medium">ID</th>
                    <th className="px-3 py-2 font-medium">Name</th>
                    <th className="px-3 py-2 font-medium">Manufacturer</th>
                    <th className="px-3 py-2 font-medium">Price</th>
                    <th className="px-3 py-2 font-medium">Stock</th>
                    <th className="px-3 py-2 font-medium">Updated</th>
                    <th className="px-3 py-2 font-medium"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {products.map((p) => (
                    <>
                      <tr key={p.id} className="hover:bg-gray-50">
                        <td className="px-3 py-2 text-gray-400">{p.id}</td>
                        <td className="px-3 py-2 font-medium text-gray-800">{p.name}</td>
                        <td className="px-3 py-2 text-gray-500">{p.manufacturer}</td>
                        <td className="px-3 py-2">${Number(p.base_price).toFixed(2)}</td>
                        <td className="px-3 py-2">
                          <span className={p.stock_quantity === 0 ? 'text-red-500' : 'text-gray-700'}>
                            {p.stock_quantity}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-gray-400 text-xs">
                          {p.updated_at ? new Date(p.updated_at).toLocaleDateString() : '—'}
                        </td>
                        <td className="px-3 py-2">
                          <div className="flex gap-2">
                            <button
                              onClick={() => editId === p.id ? setEditId(null) : startEdit(p)}
                              className="text-xs text-indigo-600 hover:text-indigo-800 focus:outline-none focus:ring-1 focus:ring-indigo-400 rounded"
                            >
                              {editId === p.id ? 'Cancel' : 'Edit'}
                            </button>
                            <button
                              onClick={() => handleDelete(p.id)}
                              className="text-xs text-red-500 hover:text-red-700 focus:outline-none focus:ring-1 focus:ring-red-400 rounded"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                      {editId === p.id && (
                        <tr key={`edit-${p.id}`}>
                          <td colSpan={7} className="px-3 py-2">
                            <ProductForm
                              form={editForm}
                              setForm={setEditForm}
                              onSubmit={handleEdit}
                              submitLabel="Save"
                              error={editError}
                              onCancel={() => setEditId(null)}
                            />
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
              {products.length === 0 && !prodLoading && (
                <p className="text-center text-gray-400 text-sm py-8">No products yet.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Orders tab ───────────────────────────────────────────────────── */}
      {tab === 'orders' && (
        <div>
          {ordLoading ? (
            <p className="text-gray-500 text-sm">Loading…</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs text-gray-500 uppercase tracking-wide">
                    <th className="px-3 py-2 font-medium">ID</th>
                    <th className="px-3 py-2 font-medium">User ID</th>
                    <th className="px-3 py-2 font-medium">Status</th>
                    <th className="px-3 py-2 font-medium">Total</th>
                    <th className="px-3 py-2 font-medium">Payment</th>
                    <th className="px-3 py-2 font-medium">Date</th>
                    <th className="px-3 py-2 font-medium">Items</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {orders.map((o) => (
                    <tr key={o.id} className="hover:bg-gray-50">
                      <td className="px-3 py-2 text-gray-400">{o.id}</td>
                      <td className="px-3 py-2">{o.user_id}</td>
                      <td className="px-3 py-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[o.status] || 'bg-gray-100 text-gray-600'}`}>
                          {o.status}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-semibold">${Number(o.total_amount).toFixed(2)}</td>
                      <td className="px-3 py-2 text-gray-500">{o.payment_method}</td>
                      <td className="px-3 py-2 text-gray-400 text-xs">{new Date(o.created_at).toLocaleDateString()}</td>
                      <td className="px-3 py-2 text-gray-500">{o.items.length}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {orders.length === 0 && (
                <p className="text-center text-gray-400 text-sm py-8">No orders yet.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Users tab ────────────────────────────────────────────────────── */}
      {tab === 'users' && (
        <div>
          {usrLoading ? (
            <p className="text-gray-500 text-sm">Loading…</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs text-gray-500 uppercase tracking-wide">
                    <th className="px-3 py-2 font-medium">ID</th>
                    <th className="px-3 py-2 font-medium">Email</th>
                    <th className="px-3 py-2 font-medium">Name</th>
                    <th className="px-3 py-2 font-medium">Role</th>
                    <th className="px-3 py-2 font-medium">Active</th>
                    <th className="px-3 py-2 font-medium">Registered</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-gray-50">
                      <td className="px-3 py-2 text-gray-400">{u.id}</td>
                      <td className="px-3 py-2">{u.email}</td>
                      <td className="px-3 py-2">{u.first_name} {u.last_name}</td>
                      <td className="px-3 py-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${u.role === 'admin' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600'}`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <span className={u.is_active ? 'text-green-600' : 'text-red-500'}>
                          {u.is_active ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-gray-400 text-xs">{new Date(u.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {users.length === 0 && (
                <p className="text-center text-gray-400 text-sm py-8">No users yet.</p>
              )}
            </div>
          )}
        </div>
      )}
    </main>
  )
}
