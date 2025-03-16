import React from 'react';
import { Table, Tag, Button, Space, Card } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { fetchQuotes } from '../../../services/api/quotes';
import { Quote } from '../../../types/quote';
import { useNavigate } from 'react-router-dom';

const statusColors = {
  pending: 'gold',
  approved: 'green',
  rejected: 'red',
};

export const QuoteList: React.FC = () => {
  const navigate = useNavigate();
  const { data: quotes, isLoading } = useQuery(['quotes'], fetchQuotes);

  const columns = [
    {
      title: 'Quote ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Vehicle',
      key: 'vehicle',
      render: (quote: Quote) => (
        `${quote.vehicleDetails.year} ${quote.vehicleDetails.make} ${quote.vehicleDetails.model}`
      ),
    },
    {
      title: 'Coverage',
      dataIndex: ['coverage', 'type'],
      key: 'coverage',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: keyof typeof statusColors) => (
        <Tag color={statusColors[status]}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Total Cost',
      dataIndex: 'totalCost',
      key: 'totalCost',
      render: (amount: number) => `$${amount.toLocaleString()}`,
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (quote: Quote) => (
        <Space>
          <Button 
            type="primary" 
            onClick={() => navigate(`/client/quotes/${quote.id}`)}
          >
            View Details
          </Button>
          {quote.status === 'pending' && (
            <Button type="default">
              Edit
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card title="My Quotes">
      <Table
        columns={columns}
        dataSource={quotes}
        rowKey="id"
        loading={isLoading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} quotes`,
        }}
      />
    </Card>
  );
};
