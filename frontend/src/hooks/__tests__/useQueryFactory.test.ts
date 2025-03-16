import { renderHook, act } from '@testing-library/react-hooks';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createQueryHook, createMutationHook, createResourceHooks } from '../useQueryFactory';
import { message } from 'antd';
import { ApiClient } from '../../services/api/apiClient';

jest.mock('antd', () => ({
  message: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('Query Factory Hooks', () => {
  let queryClient: QueryClient;
  let wrapper: React.FC<{ children: React.ReactNode }>;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
    jest.clearAllMocks();
  });

  describe('createQueryHook', () => {
    it('creates a working query hook', async () => {
      const mockFetchFn = jest.fn().mockResolvedValue({ data: 'test' });
      const useTestQuery = createQueryHook({
        queryKey: ['test'],
        fetchFn: mockFetchFn,
      });

      const { result, waitFor } = renderHook(() => useTestQuery(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual({ data: 'test' });
      });
      expect(mockFetchFn).toHaveBeenCalled();
    });

    it('handles query errors', async () => {
      const mockError = new Error('Test error');
      const mockFetchFn = jest.fn().mockRejectedValue(mockError);
      const useTestQuery = createQueryHook({
        queryKey: ['test'],
        fetchFn: mockFetchFn,
      });

      const { result, waitFor } = renderHook(() => useTestQuery(), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe(mockError);
      });
    });
  });

  describe('createMutationHook', () => {
    it('creates a working mutation hook', async () => {
      const mockMutateFn = jest.fn().mockResolvedValue({ data: 'test' });
      const useTestMutation = createMutationHook({
        mutationFn: mockMutateFn,
        invalidateQueries: ['test'],
      });

      const { result } = renderHook(() => useTestMutation(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ test: 'data' });
      });

      expect(mockMutateFn).toHaveBeenCalledWith({ test: 'data' });
      expect(message.success).toHaveBeenCalled();
    });

    it('handles mutation errors', async () => {
      const mockError = new Error('Test error');
      const mockMutateFn = jest.fn().mockRejectedValue(mockError);
      const useTestMutation = createMutationHook({
        mutationFn: mockMutateFn,
      });

      const { result } = renderHook(() => useTestMutation(), { wrapper });

      await act(async () => {
        try {
          await result.current.mutateAsync({ test: 'data' });
        } catch (error) {
          expect(message.error).toHaveBeenCalled();
        }
      });
    });
  });

  describe('createResourceHooks', () => {
    const mockApiClient = {
      get: jest.fn(),
      post: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
    } as unknown as ApiClient;

    const {
      useList,
      useItem,
      useCreate,
      useUpdate,
      useDelete,
    } = createResourceHooks('test-resource', mockApiClient);

    it('creates list hook', async () => {
      mockApiClient.get.mockResolvedValueOnce([{ id: 1, name: 'test' }]);
      const { result, waitFor } = renderHook(() => useList(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual([{ id: 1, name: 'test' }]);
      });
      expect(mockApiClient.get).toHaveBeenCalledWith('/test-resource');
    });

    it('creates item hook', async () => {
      mockApiClient.get.mockResolvedValueOnce({ id: 1, name: 'test' });
      const { result, waitFor } = renderHook(() => useItem(1)(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual({ id: 1, name: 'test' });
      });
      expect(mockApiClient.get).toHaveBeenCalledWith('/test-resource/1');
    });

    it('creates create hook', async () => {
      mockApiClient.post.mockResolvedValueOnce({ id: 1, name: 'test' });
      const { result } = renderHook(() => useCreate(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ name: 'test' });
      });

      expect(mockApiClient.post).toHaveBeenCalledWith('/test-resource', { name: 'test' });
    });

    it('creates update hook', async () => {
      mockApiClient.patch.mockResolvedValueOnce({ id: 1, name: 'updated' });
      const { result } = renderHook(() => useUpdate(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ id: 1, name: 'updated' });
      });

      expect(mockApiClient.patch).toHaveBeenCalledWith('/test-resource/1', { name: 'updated' });
    });

    it('creates delete hook', async () => {
      mockApiClient.delete.mockResolvedValueOnce(undefined);
      const { result } = renderHook(() => useDelete(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync(1);
      });

      expect(mockApiClient.delete).toHaveBeenCalledWith('/test-resource/1');
    });
  });
});
