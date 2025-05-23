import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api/client';
import { Quote } from '../types/quote';

const fetchQuotes = async (): Promise<Quote[]> => {
  const { data } = await apiClient.get('/admin/quotes');
  return data;
};

export const useAdminQuotes = () => {
  return useQuery({ queryKey: ['adminQuotes'], queryFn: fetchQuotes });
};

export const useApproveQuote = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.post(`/admin/quotes/${id}/approve`);
      return data as Quote;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminQuotes'] });
    },
  });
};

export const useDeleteAdminQuote = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/quotes/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminQuotes'] });
    },
  });
};
