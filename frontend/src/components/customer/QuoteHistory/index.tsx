import React from 'react';
import { Table, Tag } from 'antd';
import { Link } from 'react-router-dom';
import { Quote } from '../../../types/quote';
interface Props {
  quotes?: Quote[];
  loading?: boolean;
  emptyText?: string;
}
import { Card, Typography, Table, Tag } from 'antd';
import { Quote } from '../../../types/quote';

const { Title } = Typography;

export const QuoteHistory: React.FC<Props> = ({ quotes = [], loading, emptyText }) => {
  const columns = [
    {
      title: 'Quote #',
      dataIndex: 'quote_number',
      key: 'quote_number',
      render: (_: any, record: Quote) => (
        <Link to={`/client/quotes/${record.id}`}>{record.quote_number}</Link>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'accepted' ? 'green' : status === 'rejected' ? 'red' : 'gold'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Total',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount: number) => `$${amount.toFixed(2)}`,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={quotes}
      rowKey="id"
      loading={loading}
      pagination={false}
      locale={{ emptyText }}
    />
  );
export interface QuoteHistoryProps {
  quotes?: Quote[];
  loading?: boolean;
  emptyText?: string;
}

export const QuoteHistory: React.FC<QuoteHistoryProps> = ({
  quotes = [],
  loading = false,
  emptyText = 'No quotes',
}) => {
  const columns = [
    {
      title: 'Quote #',
      dataIndex: 'quote_number',
      key: 'quote_number',
    },
    {
      title: 'Service',
      dataIndex: 'service_type',
      key: 'service_type',
      render: (text: string) => text?.toUpperCase(),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'accepted' ? 'green' : status === 'pending' ? 'orange' : 'red'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
    },
  ];

  return (
    <Card>
      <Title level={2}>Quote History</Title>
      <Table
        rowKey="id"
        dataSource={quotes}
        columns={columns}
        loading={loading}
        pagination={false}
        locale={{ emptyText }}
      />
    </Card>
  );
};

export default QuoteHistory;
