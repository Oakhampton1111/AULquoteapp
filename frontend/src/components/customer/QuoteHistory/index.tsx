import React from 'react';
import { Card, Typography, Table, Tag } from 'antd';

const { Title } = Typography;

export const QuoteHistory: React.FC = () => {
  return (
    <Card>
      <Title level={2}>Quote History</Title>
      <Table 
        dataSource={[]}
        columns={[
          {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
          },
          {
            title: 'Vehicle',
            dataIndex: 'vehicle',
            key: 'vehicle',
            render: (_, record: any) => (
              <span>{record.make} {record.model} ({record.year})</span>
            ),
          },
          {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => (
              <Tag color={status === 'active' ? 'green' : status === 'pending' ? 'orange' : 'red'}>
                {status.toUpperCase()}
              </Tag>
            ),
          },
          {
            title: 'Created',
            dataIndex: 'createdAt',
            key: 'createdAt',
          },
        ]}
      />
    </Card>
  );
};

export default QuoteHistory;
