import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { message } from 'antd';
import { ApiClient } from '../services/api/apiClient';

interface QueryConfig<T> {
  queryKey: string[];
  fetchFn: () => Promise<T>;
  options?: Omit<UseQueryOptions<T, AxiosError>, 'queryKey' | 'queryFn'>;
}

interface MutationConfig<T, V> {
  mutationFn: (variables: V) => Promise<T>;
  onSuccess?: (data: T, variables: V) => void | Promise<void>;
  onError?: (error: AxiosError, variables: V) => void | Promise<void>;
  invalidateQueries?: string[];
}

export function createQueryHook<T>(config: QueryConfig<T>) {
  return () => {
    return useQuery<T, AxiosError>({
      queryKey: config.queryKey,
      queryFn: config.fetchFn,
      ...config.options,
    });
  };
}

export function createMutationHook<T, V = any>(config: MutationConfig<T, V>) {
  return () => {
    const queryClient = useQueryClient();

    return useMutation<T, AxiosError, V>({
      mutationFn: config.mutationFn,
      onSuccess: async (data, variables) => {
        if (config.invalidateQueries) {
          await Promise.all(
            config.invalidateQueries.map((key) =>
              queryClient.invalidateQueries({ queryKey: [key] })
            )
          );
        }
        message.success('Operation completed successfully');
        if (config.onSuccess) {
          await config.onSuccess(data, variables);
        }
      },
      onError: async (error, variables) => {
        message.error(error.response?.data?.message || 'Operation failed');
        if (config.onError) {
          await config.onError(error, variables);
        }
      },
    });
  };
}

// Example usage for a resource (e.g., customers)
export function createResourceHooks<T extends { id: number }>(
  resourceName: string,
  apiClient: ApiClient
) {
  const useList = createQueryHook<T[]>({
    queryKey: [resourceName],
    fetchFn: () => apiClient.get(`/${resourceName}`),
  });

  const useItem = (id: number) =>
    createQueryHook<T>({
      queryKey: [resourceName, id.toString()],
      fetchFn: () => apiClient.get(`/${resourceName}/${id}`),
    })();

  const useCreate = createMutationHook<T, Omit<T, 'id'>>({
    mutationFn: (data) => apiClient.post(`/${resourceName}`, data),
    invalidateQueries: [resourceName],
  });

  const useUpdate = createMutationHook<T, Partial<T> & { id: number }>({
    mutationFn: ({ id, ...data }) => apiClient.patch(`/${resourceName}/${id}`, data),
    invalidateQueries: [resourceName],
  });

  const useDelete = createMutationHook<void, number>({
    mutationFn: (id) => apiClient.delete(`/${resourceName}/${id}`),
    invalidateQueries: [resourceName],
  });

  return {
    useList,
    useItem,
    useCreate,
    useUpdate,
    useDelete,
  };
}
