import { useQuery } from '@tanstack/react-query';
import { fetchRateCards } from '../services/api/rateCards';
import { RateCard } from '../types/rateCard';

/**
 * Hook to fetch and manage rate cards
 */
export const useRateCards = () => {
  const queryResult = useQuery<RateCard[]>({
    queryKey: ['rateCards'],
    queryFn: () => fetchRateCards(),
  });

  const rateCards = queryResult.data ?? [];

  // Determine the currently active rate card. Fallback to the first card if none
  // are explicitly marked as active.
  const currentRateCard =
    rateCards.find(rc => rc.isActive) ?? rateCards[0] ?? undefined;

  return {
    ...queryResult,
    data: rateCards,
    rateCards,
    currentRateCard,
  };
};

export default useRateCards;
