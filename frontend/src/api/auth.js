import apiClient from './client.js';

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
