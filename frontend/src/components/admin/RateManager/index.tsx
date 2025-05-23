import React from 'react';
import { Tag, Typography } from 'antd';
import { CRUDManager } from '../../common/CRUDManager';
import { RateForm } from '../forms/RateForm';
import {
  useAdminRates,
  useCreateRate,
  useUpdateRate,
  useDeleteRate,
} from '../../../hooks/useAdminRates';
import { Rate } from '../../../types/rate';

const { Text } = Typography;

const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    render: (text: string) => <Text strong>{text}</Text>,
  },
  {
    title: 'Category',
    dataIndex: 'category',
    key: 'category',
  },
  {
    title: 'Rate',
    dataIndex: 'rate',
    key: 'rate',
    render: (value: number) => <Text>$ {value.toFixed(2)}</Text>,
  },
  {
    title: 'Unit',
    dataIndex: 'unit',
    key: 'unit',
  },
  {
    title: 'Status',
    dataIndex: 'is_active',
    key: 'is_active',
    render: (active: boolean) => (
      <Tag color={active ? 'green' : 'orange'}>{active ? 'ACTIVE' : 'INACTIVE'}</Tag>
    ),
  },
];

export const RateManager: React.FC = () => {
  const createRate = useCreateRate();
  const updateRate = useUpdateRate();
  const deleteRate = useDeleteRate();

  return (
    <CRUDManager<Rate>
      title="Rate Management"
      useQuery={useAdminRates}
      columns={columns}
      createMutation={createRate.mutateAsync}
      updateMutation={async ({ id, ...data }) => updateRate.mutateAsync({ id, data })}
      deleteMutation={deleteRate.mutateAsync}
      FormComponent={RateForm}
      queryKey={['adminRates']}
      addButtonText="Add Rate"
      deleteConfirmText="Are you sure you want to delete this rate?"
    />
  );
};

export default RateManager;
