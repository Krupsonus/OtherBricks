import apiClient from './client'

export const getReviews = (productId) => apiClient.get(`/products/${productId}/reviews`)
export const submitReview = (productId, payload) => apiClient.post(`/products/${productId}/reviews`, payload)
export const deleteReview = (reviewId) => apiClient.delete(`/reviews/${reviewId}`)
