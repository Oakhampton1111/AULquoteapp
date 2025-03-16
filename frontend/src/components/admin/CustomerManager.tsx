import React from 'react';
import { Tag, Typography } from 'antd';
import { CRUDManager } from '../common/CRUDManager';
import { CustomerForm } from './forms/CustomerForm';
import {
  useCustomers,
  useCreateCustomer,
  useUpdateCustomer,
  useDeleteCustomer,
} from '../../hooks/useCustomers';
import { Customer } from '../../types/customer';

const { Text } = Typography;

const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    render: (text: string) => <Text strong>{text}</Text>,
  },
  {
    title: 'Email',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: 'Phone',
    dataIndex: 'phone',
    key: 'phone',
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
    render: (status: string) => (
      <Tag color={status === 'active' ? 'green' : 'orange'}>
        {status.toUpperCase()}
      </Tag>
    ),
  },
];

export const CustomerManager: React.FC = () => {
  const createCustomer = useCreateCustomer();
  const updateCustomer = useUpdateCustomer();
  const deleteCustomer = useDeleteCustomer();

  return (
    <CRUDManager<Customer>
      title="Customer Management"
      useQuery={useCustomers}
      columns={columns}
      createMutation={createCustomer.mutateAsync}
      updateMutation={updateCustomer.mutateAsync}
      deleteMutation={deleteCustomer.mutateAsync}
      FormComponent={CustomerForm}
      queryKey={['customers']}
      addButtonText="Add Customer"
      deleteConfirmText="Are you sure you want to delete this customer?"
    />
  );
};
