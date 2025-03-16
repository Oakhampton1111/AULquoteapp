import { createResourceHooks } from './useQueryFactory';
import apiClient from '../services/api/apiClient';
import { Quote, QuoteCreate, QuoteFilter, QuoteStatusUpdate } from '../types/quote';
import { useMutation, useQuery } from '@tanstack/react-query';

// Create base CRUD hooks
const {
  useList: useQuotesList,
  useItem: useQuoteItem,
  useCreate: useCreateQuoteBase,
  useUpdate: useUpdateQuoteBase,
  useDelete: useDeleteQuote,
} = createResourceHooks<Quote>('quotes', apiClient);

// Extended hooks for specific quote operations
export const useQuotes = (filters?: QuoteFilter) => {
  return useQuery({
    queryKey: ['quotes', filters],
    queryFn: () => apiClient.get<Quote[]>('/quotes', { params: filters }),
  });
};

export const useQuote = (id: number) => useQuoteItem(id);

export const useCreateQuote = () => useCreateQuoteBase();

export const useUpdateQuoteStatus = () => {
  return useMutation({
    mutationFn: async ({ id, status }: QuoteStatusUpdate) =>
      apiClient.patch<Quote>(`/quotes/${id}/status`, { status }),
    onSuccess: () => {
      // Invalidate quotes list
      apiClient.invalidateQueries(['quotes']);
    },
  });
};

export const useGenerateQuote = () => {
  return useMutation({
    mutationFn: async (data: { customerId: number; requirements: string }) =>
      apiClient.post<Quote>('/quotes/generate', data),
  });
};

export { useDeleteQuote };
