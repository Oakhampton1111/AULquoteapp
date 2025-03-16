import apiClient from './client';
import { Quote, QuoteCreate, QuoteFilter, QuoteStatusUpdate } from '../../types/quote';

const API_URL = import.meta.env.VITE_API_URL;

export const createQuote = async (quoteData: QuoteCreate): Promise<Quote> => {
  const { data } = await apiClient.post('/quotes', quoteData);
  return data;
};

export const fetchQuotes = async (filters?: QuoteFilter): Promise<Quote[]> => {
  const { data } = await apiClient.get('/quotes', { params: filters });
  return data;
};

export const fetchQuoteById = async (quoteId: number): Promise<Quote> => {
  const { data } = await apiClient.get(`/quotes/${quoteId}`);
  return data;
};

export const updateQuoteStatus = async (
  quoteId: number,
  statusUpdate: QuoteStatusUpdate
): Promise<Quote> => {
  const { data } = await apiClient.patch(`/quotes/${quoteId}/status`, statusUpdate);
  return data;
};

export const deleteQuote = async (quoteId: number): Promise<void> => {
  await apiClient.delete(`/quotes/${quoteId}`);
};

export interface QuoteGenerateRequest {
  customerId: number;
  requirements: string;
}

export const generateQuote = async (request: QuoteGenerateRequest): Promise<Quote> => {
  const { data } = await apiClient.post('/admin/quotes/generate', request);
  return data;
};
