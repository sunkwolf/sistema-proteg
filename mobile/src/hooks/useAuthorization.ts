import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as authzApi from '@/api/authorization';
import { ReviewAction, CashConfirmationSubmit } from '@/types';

export function useGerenteDashboard() {
  return useQuery({
    queryKey: ['authorization', 'dashboard'],
    queryFn: authzApi.getGerenteDashboard,
    refetchInterval: 1000 * 60 * 5,
  });
}

export function usePendingProposals(params?: { collector_id?: number; page?: number }) {
  return useQuery({
    queryKey: ['authorization', 'proposals', params],
    queryFn: () => authzApi.getPendingProposals(params),
  });
}

export function useProposalDetail(id: number) {
  return useQuery({
    queryKey: ['authorization', 'proposal', id],
    queryFn: () => authzApi.getProposalDetail(id),
    enabled: id > 0,
  });
}

export function useReviewProposal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, action }: { id: number; action: ReviewAction }) =>
      authzApi.reviewProposal(id, action),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['authorization'] });
    },
  });
}

export function useCashToConfirm() {
  return useQuery({
    queryKey: ['authorization', 'cash'],
    queryFn: authzApi.getCashToConfirm,
  });
}

export function useConfirmCash() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CashConfirmationSubmit) => authzApi.confirmCash(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['authorization'] });
    },
  });
}
