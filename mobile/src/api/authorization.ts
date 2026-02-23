import api from './client';
import {
  ApiResponse,
  DashboardGerente,
  ProposalReview,
  ReviewAction,
  CashConfirmation,
  CashConfirmationSubmit,
  CashConfirmationResult,
} from '@/types';

export async function getGerenteDashboard(): Promise<DashboardGerente> {
  const { data } = await api.get<ApiResponse<DashboardGerente>>('/authorization/dashboard');
  return data.data;
}

export async function getPendingProposals(params?: {
  collector_id?: number;
  page?: number;
}): Promise<ProposalReview[]> {
  const { data } = await api.get<ApiResponse<ProposalReview[]>>('/authorization/proposals', { params });
  return data.data;
}

export async function getProposalDetail(id: number): Promise<ProposalReview> {
  const { data } = await api.get<ApiResponse<ProposalReview>>(`/authorization/proposals/${id}`);
  return data.data;
}

export async function reviewProposal(id: number, action: ReviewAction): Promise<void> {
  await api.post(`/authorization/proposals/${id}/review`, action);
}

export async function getCashToConfirm(): Promise<CashConfirmation[]> {
  const { data } = await api.get<ApiResponse<CashConfirmation[]>>('/authorization/cash');
  return data.data;
}

export async function confirmCash(payload: CashConfirmationSubmit): Promise<CashConfirmationResult> {
  const { data } = await api.post<ApiResponse<CashConfirmationResult>>('/authorization/cash/confirm', payload);
  return data.data;
}
