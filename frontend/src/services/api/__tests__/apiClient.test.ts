import { ApiClient, createApiClient } from '../apiClient';
import axios from 'axios';
import { message } from 'antd';

jest.mock('axios');
jest.mock('antd', () => ({
  message: {
    error: jest.fn(),
  },
}));

const mockAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = createApiClient({
      baseURL: 'http://test-api.com',
    });
    jest.clearAllMocks();
  });

  it('creates an instance with correct configuration', () => {
    expect(mockAxios.create).toHaveBeenCalledWith({
      baseURL: 'http://test-api.com',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  describe('HTTP methods', () => {
    const mockResponse = {
      data: {
        data: { id: 1, name: 'Test' },
        status: 200,
      },
    };

    beforeEach(() => {
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue(mockResponse),
        post: jest.fn().mockResolvedValue(mockResponse),
        put: jest.fn().mockResolvedValue(mockResponse),
        patch: jest.fn().mockResolvedValue(mockResponse),
        delete: jest.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() },
        },
      } as any);
    });

    it('handles GET requests', async () => {
      const client = createApiClient({ baseURL: 'http://test-api.com' });
      const result = await client.get('/test');
      expect(result).toEqual({ id: 1, name: 'Test' });
    });

    it('handles POST requests', async () => {
      const client = createApiClient({ baseURL: 'http://test-api.com' });
      const result = await client.post('/test', { name: 'Test' });
      expect(result).toEqual({ id: 1, name: 'Test' });
    });

    it('handles PUT requests', async () => {
      const client = createApiClient({ baseURL: 'http://test-api.com' });
      const result = await client.put('/test/1', { name: 'Updated' });
      expect(result).toEqual({ id: 1, name: 'Test' });
    });

    it('handles PATCH requests', async () => {
      const client = createApiClient({ baseURL: 'http://test-api.com' });
      const result = await client.patch('/test/1', { name: 'Updated' });
      expect(result).toEqual({ id: 1, name: 'Test' });
    });

    it('handles DELETE requests', async () => {
      const client = createApiClient({ baseURL: 'http://test-api.com' });
      const result = await client.delete('/test/1');
      expect(result).toEqual({ id: 1, name: 'Test' });
    });
  });

  describe('Error handling', () => {
    it('shows error message on request failure', async () => {
      const errorResponse = {
        response: {
          data: {
            message: 'Test error message',
          },
        },
      };

      mockAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(errorResponse),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() },
        },
      } as any);

      const client = createApiClient({ baseURL: 'http://test-api.com' });

      try {
        await client.get('/test');
      } catch (error) {
        expect(message.error).toHaveBeenCalledWith('Test error message');
      }
    });
  });
});
