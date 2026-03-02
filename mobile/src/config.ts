// Base URL del backend — sistema.protegrt.com con API bajo /api/v1
// En desarrollo local, sobreescribir con EXPO_PUBLIC_API_URL
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://sistema.protegrt.com/api/v1';

export const AUTH = {
  TOKEN_KEY: 'protegrt_token',
  REFRESH_KEY: 'protegrt_refresh',
  USER_KEY: 'protegrt_user',
};

export const CASH_LIMIT_DEFAULT = 5000; // MXN — tope default de efectivo
