import api from './client';
import {
  ApiResponse,
  DashboardCobrador,
  FolioCard,
  FolioDetail,
  Proposal,
  ProposalCreate,
  VisitNotice,
  VisitNoticeCreate,
  CashPending,
  RouteStop,
} from '@/types';

// ── Dashboard ───────────────────────────
export async function getDashboard(): Promise<DashboardCobrador> {
  const { data } = await api.get<ApiResponse<DashboardCobrador>>('/collections/dashboard');
  return data.data;
}

// ── Folios ──────────────────────────────
export async function getFolios(params?: {
  status?: string;
  search?: string;
  sort?: string;
  page?: number;
}): Promise<{ items: FolioCard[]; total: number }> {
  const { data } = await api.get<ApiResponse<FolioCard[]>>('/collections/cards', { params });
  return { items: data.data, total: data.meta?.total ?? 0 };
}

export async function getFolioDetail(folio: string): Promise<FolioDetail> {
  const { data } = await api.get<ApiResponse<FolioDetail>>(`/collections/cards/${folio}`);
  return data.data;
}

// ── Propuestas ──────────────────────────
export async function createProposal(payload: ProposalCreate): Promise<Proposal> {
  const { data } = await api.post<ApiResponse<Proposal>>('/collections/proposals', payload);
  return data.data;
}

export async function getMyProposals(params?: {
  status?: string;
  date?: string;
}): Promise<Proposal[]> {
  const { data } = await api.get<ApiResponse<Proposal[]>>('/collections/proposals/mine', { params });
  return data.data;
}

// ── Avisos de Visita ────────────────────
export async function createVisitNotice(payload: VisitNoticeCreate): Promise<VisitNotice> {
  const { data } = await api.post<ApiResponse<VisitNotice>>('/collections/visits', payload);
  return data.data;
}

// ── Efectivo ────────────────────────────
export async function getCashPending(): Promise<CashPending> {
  const { data } = await api.get<ApiResponse<CashPending>>('/collections/cash');
  return data.data;
}

// ── Ruta ────────────────────────────────
export async function getRoute(): Promise<RouteStop[]> {
  const { data } = await api.get<ApiResponse<RouteStop[]>>('/collections/route');
  return data.data;
}

// ── Upload foto ─────────────────────────
export async function uploadPhoto(uri: string): Promise<string> {
  const formData = new FormData();
  const filename = uri.split('/').pop() || 'photo.jpg';
  formData.append('file', {
    uri,
    name: filename,
    type: 'image/jpeg',
  } as any);
  const { data } = await api.post<ApiResponse<{ url: string }>>('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data.data.url;
}
