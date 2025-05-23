import apiClient from './client';

// base URL is handled by apiClient

export const fetchDashboardStats = async () => {
  const { data } = await apiClient.get('/admin/dashboard/stats');
  return data;
};

export const fetchRecentQuotes = async () => {
  const { data } = await apiClient.get('/admin/quotes/recent');
  return data;
};

export const approveQuote = async (quoteId: string) => {
  const { data } = await apiClient.post(`/admin/quotes/${quoteId}/approve`);
  return data;
};
