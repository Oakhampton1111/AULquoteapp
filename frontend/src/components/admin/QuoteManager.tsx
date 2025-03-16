import React, { useState } from 'react';
import { Button, Space, Tag, Typography, Modal } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import { CRUDManager } from '../common/CRUDManager';
import { QuoteForm } from '../forms/QuoteForm';
import {
  useQuotes,
  useCreateQuote,
  useUpdateQuoteStatus,
  useDeleteQuote,
  useGenerateQuote,
} from '../../hooks/useQuotes';
import { Quote } from '../../types/quote';
import dayjs from 'dayjs';

const { Text } = Typography;

const columns = [
  {
    title: 'Customer',
    dataIndex: ['customer', 'name'],
    key: 'customer',
    render: (text: string) => <Text strong>{text}</Text>,
  },
  {
    title: 'Total Amount',
    dataIndex: 'totalAmount',
    key: 'totalAmount',
    render: (amount: number) => (
      <Text>$ {amount.toFixed(2)}</Text>
    ),
  },
  {
    title: 'Valid Period',
    key: 'validPeriod',
    render: (_: any, record: Quote) => (
      <Text>
        {dayjs(record.validFrom).format('MMM D, YYYY')} - {dayjs(record.validTo).format('MMM D, YYYY')}
      </Text>
    ),
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
    render: (status: string) => {
      const color = {
        draft: 'orange',
        pending: 'blue',
        approved: 'green',
        rejected: 'red',
      }[status] || 'default';

      return (
        <Tag color={color}>
          {status.toUpperCase()}
        </Tag>
      );
    },
  },
];

export const QuoteManager: React.FC = () => {
  const [generateModalVisible, setGenerateModalVisible] = useState(false);
  const createQuote = useCreateQuote();
  const updateStatus = useUpdateQuoteStatus();
  const deleteQuote = useDeleteQuote();
  const generateQuote = useGenerateQuote();

  const handleGenerateQuote = async (values: any) => {
    await generateQuote.mutateAsync(values);
    setGenerateModalVisible(false);
  };

  const extraActions = (
    <Button
      type="primary"
      icon={<RobotOutlined />}
      onClick={() => setGenerateModalVisible(true)}
    >
      Generate Quote
    </Button>
  );

  return (
    <>
      <CRUDManager<Quote>
        title="Quote Management"
        useQuery={useQuotes}
        columns={columns}
        createMutation={createQuote.mutateAsync}
        updateMutation={async (quote) => {
          if (quote.status) {
            return updateStatus.mutateAsync({ id: quote.id, status: quote.status });
          }
          return quote;
        }}
        deleteMutation={deleteQuote.mutateAsync}
        FormComponent={QuoteForm}
        queryKey={['quotes']}
        addButtonText="Create Quote"
        deleteConfirmText="Are you sure you want to delete this quote?"
        extraActions={extraActions}
      />

      <Modal
        title="Generate Quote with AI"
        open={generateModalVisible}
        onCancel={() => setGenerateModalVisible(false)}
        footer={null}
      >
        <QuoteForm
          mode="generate"
          onSubmit={handleGenerateQuote}
          onCancel={() => setGenerateModalVisible(false)}
        />
      </Modal>
    </>
  );
};
