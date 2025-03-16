import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export const fetchDashboardStats = async () => {
  const { data } = await axios.get(`${API_URL}/api/admin/dashboard/stats`);
  return data;
};

export const fetchRecentQuotes = async () => {
  const { data } = await axios.get(`${API_URL}/api/admin/quotes/recent`);
  return data;
};

export const approveQuote = async (quoteId: string) => {
  const { data } = await axios.post(`${API_URL}/api/admin/quotes/${quoteId}/approve`);
  return data;
};
