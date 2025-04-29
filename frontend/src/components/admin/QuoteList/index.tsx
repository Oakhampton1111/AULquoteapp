import React from 'react';
import { Card, Typography, Table } from 'antd';

const { Title } = Typography;

export const QuoteList: React.FC = () => {
  return (
    <Card>
      <Title level={2}>Admin Quote List</Title>
      <p>This is a placeholder for the Admin Quote List component.</p>
      <Table 
        dataSource={[]}
        columns={[
          {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
          },
          {
            title: 'Client',
            dataIndex: 'client',
            key: 'client',
          },
          {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
          },
          {
            title: 'Created At',
            dataIndex: 'createdAt',
            key: 'createdAt',
          },
        ]}
      />
    </Card>
  );
};

export default QuoteList;
