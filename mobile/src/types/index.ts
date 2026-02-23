// ── Auth ────────────────────────────────
export type UserRole = 'cobrador' | 'gerente_cobranza' | 'auxiliar_cobranza' | 'admin';

export interface User {
  id: number;
  name: string;
  username: string;
  role: UserRole;
  zone: string | null;
  avatar_url: string | null;
}

export interface AuthResponse {
  token: string;
  refresh_token: string;
  user: User;
  expires_in: number;
}

// ── API Response ────────────────────────
export interface ApiResponse<T> {
  ok: boolean;
  data: T;
  meta?: {
    page: number;
    per_page: number;
    total: number;
  };
}

export interface ApiError {
  ok: false;
  error: string;
  message: string;
}

// ── Dashboard ───────────────────────────
export interface DashboardCobrador {
  collector_name: string;
  date: string;
  cash_pending: string;
  cash_limit: string | null;
  cash_pct: number;
  summary: {
    collections_count: number;
    collected_amount: string;
    pending_approval: number;
    commission_today: string;
  };
  recent_notifications: Notification[];
}

export interface DashboardGerente {
  manager_name: string;
  date: string;
  pending_approvals: number;
  summary: {
    approved_count: number;
    approved_amount: string;
    rejected_count: number;
    corrected_count: number;
  };
  collectors_with_cash: number;
}

// ── Folios / Tarjetas ───────────────────
export type OverdueLevel = 'high' | 'mid' | 'low' | 'on_time' | 'collected';

export interface FolioCard {
  folio: string;
  client_name: string;
  payment_number: number;
  total_payments: number;
  amount: string;
  due_date: string;
  days_overdue: number;
  overdue_level: OverdueLevel;
  has_proposal_today: boolean;
  proposal_status: 'pendiente' | 'aprobado' | 'rechazado' | null;
}

export interface FolioDetail {
  folio: string;
  client: {
    name: string;
    phone: string;
    address: string;
    lat: number | null;
    lng: number | null;
  };
  vehicle: {
    description: string;
    plates: string;
    color: string;
  };
  policy: {
    coverage_type: string;
    start_date: string;
    end_date: string;
    status: string;
  };
  current_payment: {
    number: number;
    total: number;
    amount: string;
    due_date: string;
    days_overdue: number;
    partial_paid: string;
    partial_remaining: string;
    partial_seq: number;
  };
}

// ── Propuestas de Cobro ─────────────────
export type PaymentMethod = 'efectivo' | 'deposito' | 'transferencia';
export type ProposalStatus = 'pendiente' | 'aprobado' | 'rechazado' | 'corregido';

export interface ProposalCreate {
  folio: string;
  payment_number: number;
  amount: string;
  method: PaymentMethod;
  receipt_number: string;
  receipt_photo_url?: string;
  lat: number;
  lng: number;
  is_partial: boolean;
}

export interface Proposal {
  id: number;
  folio: string;
  client_name: string;
  payment_number: number;
  amount: string;
  method: PaymentMethod;
  receipt_number: string;
  receipt_photo_url: string | null;
  status: ProposalStatus;
  rejection_reason: string | null;
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  is_partial: boolean;
  partial_seq: number | null;
}

// ── Aviso de Visita ─────────────────────
export type VisitReason = 'no_estaba' | 'sin_efectivo' | 'pagara_despues' | 'otro';

export interface VisitNoticeCreate {
  folio: string;
  reason: VisitReason;
  reason_detail?: string;
  photo_url: string;
  lat: number;
  lng: number;
}

export interface VisitNotice {
  id: number;
  folio: string;
  client_name: string;
  reason: VisitReason;
  reason_detail: string | null;
  photo_url: string;
  created_at: string;
}

// ── Efectivo Pendiente ──────────────────
export interface CashPending {
  total: string;
  limit: string | null;
  pct: number;
  items: CashItem[];
  delivery_history: CashDelivery[];
}

export interface CashItem {
  proposal_id: number;
  folio: string;
  client_name: string;
  amount: string;
  date: string;
}

export interface CashDelivery {
  date: string;
  amount: string;
  confirmed_by: string;
}

// ── Ruta ────────────────────────────────
export interface RouteStop {
  order: number;
  folio: string;
  client_name: string;
  address: string;
  lat: number;
  lng: number;
  status: 'completed' | 'next' | 'pending';
}

// ── Notificaciones ──────────────────────
export interface Notification {
  id: number;
  type: 'aprobado' | 'rechazado' | 'corregido' | 'nueva_tarjeta' | 'ruta' | 'tope_efectivo';
  title: string;
  body: string;
  read: boolean;
  created_at: string;
  deep_link: string | null;
}

// ── Autorización (Gerente) ──────────────
export interface ProposalReview {
  id: number;
  folio: string;
  client_name: string;
  collector_name: string;
  payment_number: number;
  amount_proposed: string;
  amount_expected: string;
  amounts_match: boolean;
  method: PaymentMethod;
  receipt_number: string;
  receipt_valid: boolean;
  receipt_photo_url: string | null;
  lat: number;
  lng: number;
  created_at: string;
  is_partial: boolean;
  policy_summary: {
    coverage: string;
    vehicle: string;
  };
}

export type ReviewDecision = 'aprobar' | 'corregir' | 'rechazar';

export interface ReviewAction {
  decision: ReviewDecision;
  correction_field?: string;
  correction_value?: string;
  rejection_reason?: string;
}

// ── Confirmación de Efectivo ────────────
export interface CashConfirmation {
  collector_id: number;
  collector_name: string;
  expected_items: CashItem[];
  expected_total: string;
}

export interface CashConfirmationSubmit {
  collector_id: number;
  received_amount: string;
}

export interface CashConfirmationResult {
  expected: string;
  received: string;
  difference: string;
  has_debt: boolean;
}
