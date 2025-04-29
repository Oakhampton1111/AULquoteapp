import apiClient from './client';
import { Quote, QuoteCreate, QuoteFilter, QuoteStatusUpdate } from '../../types/quote';
import { handleApiError } from '../../utils/errorHandling';
import { notification } from 'antd';

/**
 * Create a new quote
 * @param quoteData The data for the new quote
 * @returns A promise that resolves to the created quote
 */
export const createQuote = async (quoteData: QuoteCreate): Promise<Quote> => {
  try {
    const response = await apiClient.post('/quotes', quoteData);

    // Show success notification
    notification.success({
      message: 'Quote Created',
      description: `Quote has been created successfully.`,
    });

    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, 'Failed to create quote', false);
    notification.error({
      message: 'Error Creating Quote',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Fetch all quotes with optional filters
 * @param filters Optional filters to apply to the query
 * @returns A promise that resolves to an array of quotes
 */
export const fetchQuotes = async (filters?: QuoteFilter): Promise<Quote[]> => {
  try {
    const response = await apiClient.get('/quotes', { params: filters });
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, 'Failed to fetch quotes', false);
    notification.error({
      message: 'Error Fetching Quotes',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Fetch a single quote by ID
 * @param quoteId The ID of the quote to fetch
 * @returns A promise that resolves to the quote
 */
export const fetchQuoteById = async (quoteId: number): Promise<Quote> => {
  try {
    const response = await apiClient.get(`/quotes/${quoteId}`);
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, `Failed to fetch quote #${quoteId}`, false);
    notification.error({
      message: 'Error Fetching Quote',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Update the status of a quote
 * @param quoteId The ID of the quote to update
 * @param statusUpdate The status update data
 * @returns A promise that resolves to the updated quote
 */
export const updateQuoteStatus = async (
  quoteId: number,
  statusUpdate: QuoteStatusUpdate
): Promise<Quote> => {
  try {
    const response = await apiClient.patch(`/quotes/${quoteId}/status`, statusUpdate);

    // Show success notification
    notification.success({
      message: 'Quote Updated',
      description: `Quote #${quoteId} status has been updated successfully.`,
    });

    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, `Failed to update quote #${quoteId} status`, false);
    notification.error({
      message: 'Error Updating Quote',
      description: errorMessage,
    });
    throw error;
  }
};

/**
 * Delete a quote
 * @param quoteId The ID of the quote to delete
 * @returns A promise that resolves when the quote is deleted
 */
export const deleteQuote = async (quoteId: number): Promise<void> => {
  try {
    await apiClient.delete(`/quotes/${quoteId}`);

    // Show success notification
    notification.success({
      message: 'Quote Deleted',
      description: `Quote #${quoteId} has been deleted successfully.`,
    });
  } catch (error) {
    const errorMessage = handleApiError(error, `Failed to delete quote #${quoteId}`, false);
    notification.error({
      message: 'Error Deleting Quote',
      description: errorMessage,
    });
    throw error;
  }
};

export interface QuoteGenerateRequest {
  customerId: number;
  requirements: string;
}

/**
 * Generate a quote based on customer requirements (admin only)
 * @param request The quote generation request
 * @returns A promise that resolves to the generated quote
 */
export const generateQuote = async (request: QuoteGenerateRequest): Promise<Quote> => {
  try {
    const response = await apiClient.post('/admin/quotes/generate', request);

    // Show success notification
    notification.success({
      message: 'Quote Generated',
      description: `Quote has been generated successfully for customer #${request.customerId}.`,
    });

    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error, 'Failed to generate quote', false);
    notification.error({
      message: 'Error Generating Quote',
      description: errorMessage,
    });
    throw error;
  }
};
