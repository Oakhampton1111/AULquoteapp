import apiClient from './apiClient';

export const fetchDashboardStats = async () => {
  return apiClient.get('/admin/dashboard/stats');
};

export const fetchRecentQuotes = async () => {
  return apiClient.get('/admin/quotes/recent');
};

export const approveQuote = async (quoteId: string) => {
  return apiClient.post(`/admin/quotes/${quoteId}/approve`);
};
