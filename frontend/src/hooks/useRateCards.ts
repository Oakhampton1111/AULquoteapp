import { useQuery } from '@tanstack/react-query';
import { fetchRateCards } from '../services/api/rateCards';
import { RateCard } from '../types/rateCard';

/**
 * Hook to fetch and manage rate cards
 */
export const useRateCards = () => {
  const {
    data: rateCards = [],
    isLoading,
    error,
    refetch,
  } = useQuery<RateCard[]>({
    queryKey: ['rateCards'],
    queryFn: () => fetchRateCards(),
  });

  return {
    rateCards,
    isLoading,
    error,
    refetch,
  };
};

export default useRateCards;
