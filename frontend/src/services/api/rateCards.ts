import apiClient from './client';
import { RateCard } from '../../types/rateCard';
import { handleApiError } from '../../utils/errorHandling';
import { notification } from 'antd';

/**
 * Fetch all rate cards
 * @returns A promise that resolves to an array of rate cards
 */
export const fetchRateCards = async (): Promise<RateCard[]> => {
  try {
    const response = await apiClient.get('/rate-cards');
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, 'Failed to fetch rate cards', false);
    notification.error({
      message: 'Error Fetching Rate Cards',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Fetch a single rate card by ID
 * @param id The ID of the rate card to fetch
 * @returns A promise that resolves to the rate card
 */
export const fetchRateCardById = async (id: string): Promise<RateCard> => {
  try {
    const response = await apiClient.get(`/rate-cards/${id}`);
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, `Failed to fetch rate card #${id}`, false);
    notification.error({
      message: 'Error Fetching Rate Card',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Create a new rate card
 * @param rateCard The data for the new rate card
 * @returns A promise that resolves to the created rate card
 */
export const createRateCard = async (rateCard: Omit<RateCard, 'id'>): Promise<RateCard> => {
  try {
    const response = await apiClient.post('/rate-cards', rateCard);

    // Show success notification
    notification.success({
      message: 'Rate Card Created',
      description: `Rate card "${rateCard.name}" has been created successfully.`,
    });

    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, 'Failed to create rate card', false);
    notification.error({
      message: 'Error Creating Rate Card',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Update an existing rate card
 * @param id The ID of the rate card to update
 * @param rateCard The updated data for the rate card
 * @returns A promise that resolves to the updated rate card
 */
export const updateRateCard = async (id: string, rateCard: Partial<RateCard>): Promise<RateCard> => {
  try {
    const response = await apiClient.patch(`/rate-cards/${id}`, rateCard);

    // Show success notification
    notification.success({
      message: 'Rate Card Updated',
      description: `Rate card #${id} has been updated successfully.`,
    });

    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, `Failed to update rate card #${id}`, false);
    notification.error({
      message: 'Error Updating Rate Card',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Delete a rate card
 * @param id The ID of the rate card to delete
 * @returns A promise that resolves when the rate card is deleted
 */
export const deleteRateCard = async (id: string): Promise<void> => {
  try {
    await apiClient.delete(`/rate-cards/${id}`);

    // Show success notification
    notification.success({
      message: 'Rate Card Deleted',
      description: `Rate card #${id} has been deleted successfully.`,
    });
  } catch (error) {
    const errorMessage = handleApiError(error, `Failed to delete rate card #${id}`, false);
    notification.error({
      message: 'Error Deleting Rate Card',
      description: errorMessage,
    });
    throw error;
  }
};
