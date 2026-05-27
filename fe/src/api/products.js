import apiClient from './client'

export const getProducts = (params) => apiClient.get('/products', { params })
export const getProduct = (id) => apiClient.get(`/products/${id}`)
export const getCategories = () => apiClient.get('/categories')
export const getPriceOffers = (id) => apiClient.get(`/products/${id}/offers`)
