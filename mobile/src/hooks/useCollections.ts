import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as collectionsApi from '@/api/collections';
import { ProposalCreate, VisitNoticeCreate } from '@/types';

// ── Dashboard ───────────────────────────
export function useDashboard() {
  return useQuery({
    queryKey: ['collections', 'dashboard'],
    queryFn: collectionsApi.getDashboard,
    refetchInterval: 1000 * 60 * 5, // Refresco cada 5 min
  });
}

// ── Folios ──────────────────────────────
export function useFolios(params?: { status?: string; search?: string; sort?: string; page?: number }) {
  return useQuery({
    queryKey: ['collections', 'folios', params],
    queryFn: () => collectionsApi.getFolios(params),
  });
}

export function useFolioDetail(folio: string) {
  return useQuery({
    queryKey: ['collections', 'folio', folio],
    queryFn: () => collectionsApi.getFolioDetail(folio),
    enabled: !!folio,
  });
}

// ── Propuestas ──────────────────────────
export function useMyProposals(params?: { status?: string; date?: string }) {
  return useQuery({
    queryKey: ['collections', 'proposals', 'mine', params],
    queryFn: () => collectionsApi.getMyProposals(params),
  });
}

export function useCreateProposal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ProposalCreate) => collectionsApi.createProposal(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['collections'] });
    },
  });
}

// ── Avisos ──────────────────────────────
export function useCreateVisitNotice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: VisitNoticeCreate) => collectionsApi.createVisitNotice(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['collections'] });
    },
  });
}

// ── Efectivo ────────────────────────────
export function useCashPending() {
  return useQuery({
    queryKey: ['collections', 'cash'],
    queryFn: collectionsApi.getCashPending,
  });
}

// ── Ruta ────────────────────────────────
export function useRoute() {
  return useQuery({
    queryKey: ['collections', 'route'],
    queryFn: collectionsApi.getRoute,
  });
}
