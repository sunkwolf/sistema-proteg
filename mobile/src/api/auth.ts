import api from './client';
import { AuthResponse } from '@/types';

export async function login(username: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post('/auth/login', { username, password });
  // Map backend response to AuthResponse interface
  return {
    token: data.access_token,
    refresh_token: '', // TODO: implement refresh tokens
    user: data.user || { id: 0, username, name: username, role: 'collector' },
    expires_in: data.expires_in || 900,
  };
}

export async function refreshToken(token: string): Promise<AuthResponse> {
  const { data } = await api.post('/auth/refresh', { refresh_token: token });
  return {
    token: data.access_token,
    refresh_token: data.refresh_token || '',
    user: data.user,
    expires_in: data.expires_in || 900,
  };
}
