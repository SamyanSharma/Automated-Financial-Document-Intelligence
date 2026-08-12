import apiClient from './client.js';

/**
 * POST /api/v1/auth/login  { email, password }
 * -> { access_token, token_type }
 */
export async function login(email, password) {
  const { data } = await apiClient.post('/auth/login', { email, password });
  return data;
}

export function logout() {
  localStorage.removeItem('auth_token');
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('auth_token'));
}
