import React from 'react';
import { Card, Typography, Table, Space, Button, Popconfirm, Tag } from 'antd';
import { useAdminQuotes, useApproveQuote, useDeleteAdminQuote } from '../../../hooks/useAdminQuotes';
import { Quote } from '../../../types/quote';

const { Title } = Typography;

export const QuoteList: React.FC = () => {
  const { data: quotes, isLoading } = useAdminQuotes();
  const approveQuote = useApproveQuote();
  const deleteQuote = useDeleteAdminQuote();

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <Tag>{status.toUpperCase()}</Tag>,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (record: Quote) => (
        <Space>
          {record.status !== 'approved' && (
            <Button size="small" onClick={() => approveQuote.mutate(record.id)}>
              Approve
            </Button>
          )}
          <Popconfirm
            title="Are you sure delete this quote?"
            onConfirm={() => deleteQuote.mutate(record.id)}
          >
            <Button size="small" danger>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card>
      <Title level={2}>Admin Quote List</Title>
      <Table rowKey="id" loading={isLoading} dataSource={quotes} columns={columns} />
    </Card>
  );
};

export default QuoteList;
