import React from 'react';
import { Tag, Typography } from 'antd';
import { CRUDManager } from '../common/CRUDManager';
import { RateCardForm } from './forms/RateCardForm';
import {
  useRateCards,
  useCreateRateCard,
  useUpdateRateCard,
  useDeleteRateCard,
} from '../../hooks/useRateCards';
import { RateCard } from '../../types/rateCard';
import dayjs from 'dayjs';

const { Text } = Typography;

const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    render: (text: string) => <Text strong>{text}</Text>,
  },
  {
    title: 'Description',
    dataIndex: 'description',
    key: 'description',
    ellipsis: true,
  },
  {
    title: 'Base Rate',
    dataIndex: 'baseRate',
    key: 'baseRate',
    render: (value: number) => (
      <Text>$ {value.toFixed(2)}</Text>
    ),
  },
  {
    title: 'Effective Period',
    key: 'effectivePeriod',
    render: (_: any, record: RateCard) => (
      <Text>
        {dayjs(record.effectiveFrom).format('MMM D, YYYY')} - {dayjs(record.effectiveTo).format('MMM D, YYYY')}
      </Text>
    ),
  },
  {
    title: 'Status',
    key: 'status',
    render: (_: any, record: RateCard) => {
      const now = dayjs();
      const isActive = now.isAfter(record.effectiveFrom) && now.isBefore(record.effectiveTo);
      return (
        <Tag color={isActive ? 'green' : 'orange'}>
          {isActive ? 'ACTIVE' : 'INACTIVE'}
        </Tag>
      );
    },
  },
];

export const RateCardManager: React.FC = () => {
  const createRateCard = useCreateRateCard();
  const updateRateCard = useUpdateRateCard();
  const deleteRateCard = useDeleteRateCard();

  return (
    <CRUDManager<RateCard>
      title="Rate Card Management"
      useQuery={useRateCards}
      columns={columns}
      createMutation={createRateCard.mutateAsync}
      updateMutation={updateRateCard.mutateAsync}
      deleteMutation={deleteRateCard.mutateAsync}
      FormComponent={RateCardForm}
      queryKey={['rate-cards']}
      addButtonText="Add Rate Card"
      deleteConfirmText="Are you sure you want to delete this rate card?"
    />
  );
};
