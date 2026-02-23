import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_BASE_URL, AUTH } from '@/config';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Interceptor: inyecta token en cada request
api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const token = await SecureStore.getItemAsync(AUTH.TOKEN_KEY);
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor: maneja 401 (token expirado)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // TODO: implementar refresh token
      await SecureStore.deleteItemAsync(AUTH.TOKEN_KEY);
      await SecureStore.deleteItemAsync(AUTH.REFRESH_KEY);
      await SecureStore.deleteItemAsync(AUTH.USER_KEY);
    }
    return Promise.reject(error);
  }
);

export default api;
