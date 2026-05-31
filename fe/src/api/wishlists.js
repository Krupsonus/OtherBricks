import apiClient from './client'

export const getWishlists = () => apiClient.get('/wishlists')
export const createWishlist = (name) => apiClient.post('/wishlists', { name })
export const deleteWishlist = (id) => apiClient.delete(`/wishlists/${id}`)
export const addToWishlist = (wishlistId, productId) =>
  apiClient.post(`/wishlists/${wishlistId}/products/${productId}`)
export const removeFromWishlist = (wishlistId, productId) =>
  apiClient.delete(`/wishlists/${wishlistId}/products/${productId}`)
