import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import { AUTH } from '@/config';
import { User, UserRole } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  setAuth: (user: User, token: string, refreshToken: string) => Promise<void>;
  logout: () => Promise<void>;
  restore: () => Promise<void>;
  hasRole: (role: UserRole) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isLoading: true,
  isAuthenticated: false,

  setAuth: async (user, token, refreshToken) => {
    await SecureStore.setItemAsync(AUTH.TOKEN_KEY, token);
    await SecureStore.setItemAsync(AUTH.REFRESH_KEY, refreshToken);
    await SecureStore.setItemAsync(AUTH.USER_KEY, JSON.stringify(user));
    set({ user, token, isLoading: false, isAuthenticated: true });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync(AUTH.TOKEN_KEY);
    await SecureStore.deleteItemAsync(AUTH.REFRESH_KEY);
    await SecureStore.deleteItemAsync(AUTH.USER_KEY);
    set({ user: null, token: null, isLoading: false, isAuthenticated: false });
  },

  restore: async () => {
    try {
      const token = await SecureStore.getItemAsync(AUTH.TOKEN_KEY);
      const userJson = await SecureStore.getItemAsync(AUTH.USER_KEY);
      if (token && userJson) {
        const user = JSON.parse(userJson) as User;
        set({ user, token, isLoading: false, isAuthenticated: true });
      } else {
        set({ user: null, token: null, isLoading: false, isAuthenticated: false });
      }
    } catch {
      set({ user: null, token: null, isLoading: false, isAuthenticated: false });
    }
  },

  hasRole: (role) => get().user?.role === role,
}));
