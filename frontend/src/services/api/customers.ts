import apiClient from './client';
import { Customer, CustomerCreate, CustomerFilter } from '../../types/customer';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// API functions
export const createCustomer = async (customerData: CustomerCreate): Promise<Customer> => {
  const { data } = await apiClient.post('/customers', customerData);
  return data;
};

export const fetchCustomers = async (filters?: CustomerFilter): Promise<Customer[]> => {
  const { data } = await apiClient.get('/customers', { params: filters });
  return data;
};

export const fetchCustomerById = async (customerId: number): Promise<Customer> => {
  const { data } = await apiClient.get(`/customers/${customerId}`);
  return data;
};

export const updateCustomer = async (
  customerId: number,
  customerData: Partial<CustomerCreate>
): Promise<Customer> => {
  const { data } = await apiClient.patch(`/customers/${customerId}`, customerData);
  return data;
};

export const deleteCustomer = async (customerId: number): Promise<void> => {
  await apiClient.delete(`/customers/${customerId}`);
};

// React Query Hooks
export const useCustomers = (filters?: CustomerFilter) => {
  return useQuery({
    queryKey: ['customers', filters],
    queryFn: () => fetchCustomers(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useCustomer = (customerId: number) => {
  return useQuery({
    queryKey: ['customers', customerId],
    queryFn: () => fetchCustomerById(customerId),
    staleTime: 5 * 60 * 1000,
  });
};

export const useCreateCustomer = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
  });
};

export const useUpdateCustomer = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<CustomerCreate> }) =>
      updateCustomer(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customers', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
  });
};

export const useDeleteCustomer = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
  });
};
