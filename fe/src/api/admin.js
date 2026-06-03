import apiClient from './client'

export const adminGetProducts = () => apiClient.get('/admin/products')
export const adminCreateProduct = (data) => apiClient.post('/admin/products', data)
export const adminUpdateProduct = (id, data) => apiClient.put(`/admin/products/${id}`, data)
export const adminDeleteProduct = (id) => apiClient.delete(`/admin/products/${id}`)

export const adminGetOrders = () => apiClient.get('/admin/orders')
export const adminGetUsers = () => apiClient.get('/admin/users')
