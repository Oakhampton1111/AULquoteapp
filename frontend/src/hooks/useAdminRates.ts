import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api/client';
import { Rate, RateInput } from '../types/rate';

const fetchRates = async (): Promise<Rate[]> => {
  const { data } = await apiClient.get('/admin/rates');
  return data;
};

export const useAdminRates = () => {
  return useQuery({ queryKey: ['adminRates'], queryFn: fetchRates });
};

export const useCreateRate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (rate: RateInput) => {
      const { data } = await apiClient.post('/admin/rates', rate);
      return data as Rate;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminRates'] });
    },
  });
};

export const useUpdateRate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<RateInput> }) => {
      const response = await apiClient.put(`/admin/rates/${id}`, data);
      return response.data as Rate;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminRates'] });
    },
  });
};

export const useDeleteRate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/rate-cards/rates/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminRates'] });
    },
  });
};
