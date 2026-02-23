import api from './client';
import { ApiResponse, AuthResponse } from '@/types';

export async function login(username: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post<ApiResponse<AuthResponse>>('/auth/login', {
    username,
    password,
  });
  return data.data;
}

export async function refreshToken(token: string): Promise<AuthResponse> {
  const { data } = await api.post<ApiResponse<AuthResponse>>('/auth/refresh', {
    refresh_token: token,
  });
  return data.data;
}
