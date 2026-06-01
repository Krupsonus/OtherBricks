import apiClient from './client'

export const getAlerts = () => apiClient.get('/alerts')
export const createAlert = (product_id, target_price) =>
  apiClient.post('/alerts', { product_id, target_price })
export const deleteAlert = (id) => apiClient.delete(`/alerts/${id}`)
