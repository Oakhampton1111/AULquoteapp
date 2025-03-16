import axios from 'axios';
import { RateCard } from '../../types/rateCard';

const API_URL = import.meta.env.VITE_API_URL;

export const fetchRateCards = async () => {
  const { data } = await axios.get<RateCard[]>(`${API_URL}/api/rate-cards`);
  return data;
};

export const fetchRateCardById = async (id: string) => {
  const { data } = await axios.get<RateCard>(`${API_URL}/api/rate-cards/${id}`);
  return data;
};

export const createRateCard = async (rateCard: Omit<RateCard, 'id'>) => {
  const { data } = await axios.post<RateCard>(`${API_URL}/api/rate-cards`, rateCard);
  return data;
};

export const updateRateCard = async (id: string, rateCard: Partial<RateCard>) => {
  const { data } = await axios.patch<RateCard>(`${API_URL}/api/rate-cards/${id}`, rateCard);
  return data;
};

export const deleteRateCard = async (id: string) => {
  await axios.delete(`${API_URL}/api/rate-cards/${id}`);
};
