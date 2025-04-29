import React from 'react';
import { Card, Typography, Table } from 'antd';

const { Title } = Typography;

export const RateManager: React.FC = () => {
  return (
    <Card>
      <Title level={2}>Rate Manager</Title>
      <p>This is a placeholder for the Rate Manager component.</p>
      <Table 
        dataSource={[]}
        columns={[
          {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
          },
          {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
          },
          {
            title: 'Base Cost',
            dataIndex: 'baseCost',
            key: 'baseCost',
          },
          {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
          },
        ]}
      />
    </Card>
  );
};

export default RateManager;
