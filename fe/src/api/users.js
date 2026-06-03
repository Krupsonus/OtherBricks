import apiClient from './client'

export const updateProfile = (data) => apiClient.put('/users/me', data)
