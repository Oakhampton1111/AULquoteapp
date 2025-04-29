import React from 'react';
import { Card, Typography, List, Tag, Divider } from 'antd';

const { Title, Text } = Typography;

export const RateCardViewer: React.FC = () => {
  return (
    <Card>
      <Title level={2}>Available Rate Cards</Title>
      <List
        itemLayout="vertical"
        dataSource={[
          {
            id: 'rate-1',
            name: 'Standard Storage',
            description: 'Basic coverage for stored vehicles',
            baseCost: 100,
            coverageDetails: [
              { type: 'Damage', description: 'Coverage for damage while in storage', included: true },
              { type: 'Theft', description: 'Coverage for theft while in storage', included: true }
            ],
          },
          {
            id: 'rate-2',
            name: 'Premium Storage',
            description: 'Enhanced coverage for stored vehicles',
            baseCost: 200,
            coverageDetails: [
              { type: 'Damage', description: 'Coverage for damage while in storage', included: true },
              { type: 'Theft', description: 'Coverage for theft while in storage', included: true },
              { type: 'Natural Disasters', description: 'Coverage for natural disasters', included: true }
            ],
          }
        ]}
        renderItem={(item) => (
          <List.Item>
            <Card type="inner" title={item.name}>
              <Text>{item.description}</Text>
              <Divider />
              <Text strong>Base Cost: ${item.baseCost}</Text>
              <Divider />
              <Title level={5}>Coverage Details:</Title>
              <List
                dataSource={item.coverageDetails}
                renderItem={(coverage) => (
                  <List.Item>
                    <Text>{coverage.type}: {coverage.description}</Text>
                    <Tag color={coverage.included ? 'green' : 'red'}>
                      {coverage.included ? 'Included' : 'Not Included'}
                    </Tag>
                  </List.Item>
                )}
              />
            </Card>
          </List.Item>
        )}
      />
    </Card>
  );
};

export default RateCardViewer;
