import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import { AUTH } from '@/config';
import { User, UserRole } from '@/types';
import * as authApi from '@/api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (role: UserRole) => boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Restaurar sesión al montar
  useEffect(() => {
    (async () => {
      try {
        const token = await SecureStore.getItemAsync(AUTH.TOKEN_KEY);
        const userJson = await SecureStore.getItemAsync(AUTH.USER_KEY);
        if (token && userJson) {
          const user = JSON.parse(userJson) as User;
          setState({ user, token, isLoading: false, isAuthenticated: true });
        } else {
          setState((s) => ({ ...s, isLoading: false }));
        }
      } catch {
        setState((s) => ({ ...s, isLoading: false }));
      }
    })();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const result = await authApi.login(username, password);
    await SecureStore.setItemAsync(AUTH.TOKEN_KEY, result.token);
    await SecureStore.setItemAsync(AUTH.REFRESH_KEY, result.refresh_token);
    await SecureStore.setItemAsync(AUTH.USER_KEY, JSON.stringify(result.user));
    setState({
      user: result.user,
      token: result.token,
      isLoading: false,
      isAuthenticated: true,
    });
  }, []);

  const logout = useCallback(async () => {
    await SecureStore.deleteItemAsync(AUTH.TOKEN_KEY);
    await SecureStore.deleteItemAsync(AUTH.REFRESH_KEY);
    await SecureStore.deleteItemAsync(AUTH.USER_KEY);
    setState({ user: null, token: null, isLoading: false, isAuthenticated: false });
  }, []);

  const hasRole = useCallback(
    (role: UserRole) => state.user?.role === role,
    [state.user]
  );

  return (
    <AuthContext.Provider value={{ ...state, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
