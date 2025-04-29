import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api/client';
import { notification } from 'antd';

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  createdAt: string;
}

export interface CustomerInput {
  name: string;
  email: string;
  phone: string;
}

/**
 * Hook to fetch and manage customers
 */
export const useCustomers = () => {
  const fetchCustomers = async (): Promise<Customer[]> => {
    const response = await apiClient.get('/customers');
    return response.data;
  };

  const {
    data: customers = [],
    isLoading,
    error,
    refetch,
  } = useQuery<Customer[]>({
    queryKey: ['customers'],
    queryFn: fetchCustomers,
  });

  return {
    customers,
    isLoading,
    error,
    refetch,
  };
};

/**
 * Hook to create a new customer
 */
export const useCreateCustomer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (customerData: CustomerInput) => {
      const response = await apiClient.post('/customers', customerData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      notification.success({
        message: 'Customer Created',
        description: 'Customer has been created successfully.',
      });
    },
    onError: (error: any) => {
      notification.error({
        message: 'Error Creating Customer',
        description: error.message || 'Failed to create customer.',
      });
    },
  });
};

/**
 * Hook to update an existing customer
 */
export const useUpdateCustomer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<CustomerInput> }) => {
      const response = await apiClient.patch(`/customers/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      notification.success({
        message: 'Customer Updated',
        description: 'Customer has been updated successfully.',
      });
    },
    onError: (error: any) => {
      notification.error({
        message: 'Error Updating Customer',
        description: error.message || 'Failed to update customer.',
      });
    },
  });
};

/**
 * Hook to delete a customer
 */
export const useDeleteCustomer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/customers/${id}`);
      return id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      notification.success({
        message: 'Customer Deleted',
        description: 'Customer has been deleted successfully.',
      });
    },
    onError: (error: any) => {
      notification.error({
        message: 'Error Deleting Customer',
        description: error.message || 'Failed to delete customer.',
      });
    },
  });
};

export default useCustomers;
