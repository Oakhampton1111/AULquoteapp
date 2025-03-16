import apiClient from './client';
import { Conversation, ConversationCreate, ConversationFilter } from '../../types/conversation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// API functions
export const createConversation = async (conversationData: ConversationCreate): Promise<Conversation> => {
  const { data } = await apiClient.post('/conversations', conversationData);
  return data;
};

export const fetchConversations = async (filters?: ConversationFilter): Promise<Conversation[]> => {
  const { data } = await apiClient.get('/conversations', { params: filters });
  return data;
};

export const fetchQuoteConversations = async (quoteId: number): Promise<Conversation[]> => {
  const { data } = await apiClient.get(`/quotes/${quoteId}/conversations`);
  return data;
};

export const updateConversation = async (
  conversationId: number,
  message: string
): Promise<Conversation> => {
  const { data } = await apiClient.patch(`/conversations/${conversationId}`, { message });
  return data;
};

export const deleteConversation = async (conversationId: number): Promise<void> => {
  await apiClient.delete(`/conversations/${conversationId}`);
};

// React Query Hooks with real-time updates support
export const useQuoteConversations = (quoteId: number) => {
  return useQuery({
    queryKey: ['conversations', quoteId],
    queryFn: () => fetchQuoteConversations(quoteId),
    refetchInterval: 5000, // Poll every 5 seconds for new messages
    staleTime: 0, // Always fetch fresh data
  });
};

export const useCreateConversation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createConversation,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ 
        queryKey: ['conversations', data.quote_id] 
      });
    },
    // Optimistic update
    onMutate: async (newConversation) => {
      await queryClient.cancelQueries({ 
        queryKey: ['conversations', newConversation.quote_id] 
      });

      const previousConversations = queryClient.getQueryData<Conversation[]>([
        'conversations',
        newConversation.quote_id,
      ]);

      queryClient.setQueryData<Conversation[]>(
        ['conversations', newConversation.quote_id],
        (old = []) => [
          ...old,
          {
            ...newConversation,
            id: Math.random(), // Temporary ID
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ]
      );

      return { previousConversations };
    },
    onError: (_, __, context) => {
      if (context?.previousConversations) {
        queryClient.setQueryData(
          ['conversations', context.previousConversations[0]?.quote_id],
          context.previousConversations
        );
      }
    },
  });
};

export const useUpdateConversation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, message }: { id: number; message: string }) =>
      updateConversation(id, message),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ 
        queryKey: ['conversations', data.quote_id] 
      });
    },
  });
};

export const useDeleteConversation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteConversation,
    onSuccess: (_, conversationId) => {
      // Invalidate and refetch conversations queries
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};
