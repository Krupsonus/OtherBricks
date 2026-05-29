import apiClient from './client'

export const placeOrder = (payload) => apiClient.post('/orders', payload)
export const getOrders = () => apiClient.get('/orders')
export const getOrderDetail = (id) => apiClient.get(`/orders/${id}`)
