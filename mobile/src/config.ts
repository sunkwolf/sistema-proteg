// Base URL del backend — se sobreescribe con variable de entorno en producción
// Por ahora apunta al VPS vía WireGuard (pendiente de configurar)
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const AUTH = {
  TOKEN_KEY: 'protegrt_token',
  REFRESH_KEY: 'protegrt_refresh',
  USER_KEY: 'protegrt_user',
};

export const CASH_LIMIT_DEFAULT = 5000; // MXN — tope default de efectivo
