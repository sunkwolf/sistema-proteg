import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import { AUTH } from '@/config';
import { User, UserRole } from '@/types';

// Web fallback: SecureStore no funciona en web, usar localStorage
const storage = {
  getItem: async (key: string): Promise<string | null> => {
    if (Platform.OS === 'web') return localStorage.getItem(key);
    return SecureStore.getItemAsync(key);
  },
  setItem: async (key: string, value: string): Promise<void> => {
    if (Platform.OS === 'web') { localStorage.setItem(key, value); return; }
    await SecureStore.setItemAsync(key, value);
  },
  deleteItem: async (key: string): Promise<void> => {
    if (Platform.OS === 'web') { localStorage.removeItem(key); return; }
    await SecureStore.deleteItemAsync(key);
  },
};

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
    await storage.setItem(AUTH.TOKEN_KEY, token);
    await storage.setItem(AUTH.REFRESH_KEY, refreshToken);
    await storage.setItem(AUTH.USER_KEY, JSON.stringify(user));
    set({ user, token, isLoading: false, isAuthenticated: true });
  },

  logout: async () => {
    await storage.deleteItem(AUTH.TOKEN_KEY);
    await storage.deleteItem(AUTH.REFRESH_KEY);
    await storage.deleteItem(AUTH.USER_KEY);
    set({ user: null, token: null, isLoading: false, isAuthenticated: false });
  },

  restore: async () => {
    try {
      const token = await storage.getItem(AUTH.TOKEN_KEY);
      const userJson = await storage.getItem(AUTH.USER_KEY);
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
