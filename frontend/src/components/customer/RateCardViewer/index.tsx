import React from 'react';
import { Card, Typography, List, Tag, Divider } from 'antd';
import { RateCard } from '../../../types/rateCard';

const { Title, Text } = Typography;

export interface RateCardViewerProps {
  rateCard: RateCard;
}

export const RateCardViewer: React.FC<RateCardViewerProps> = ({ rateCard }) => {
  const {
    name,
    description,
    baseCost,
    coverageDetails,
    durationOptions,
    restrictions,
  } = rateCard;

  return (
    <Card>
      <Title level={3}>{name}</Title>
      <Text>{description}</Text>
      <Divider />
      <Text strong>Base Cost: ${baseCost}</Text>
      {coverageDetails?.length > 0 && (
        <>
          <Divider />
          <Title level={5}>Coverage Details:</Title>
          <List
            dataSource={coverageDetails}
            renderItem={(coverage) => (
              <List.Item>
                <Text>
                  {coverage.type}: {coverage.description}
                </Text>
                <Tag color={coverage.included ? 'green' : 'red'}>
                  {coverage.included ? 'Included' : 'Not Included'}
                </Tag>
              </List.Item>
            )}
          />
        </>
      )}
      {durationOptions?.length > 0 && (
        <>
          <Divider />
          <Title level={5}>Duration Options:</Title>
          <List
            dataSource={durationOptions}
            renderItem={(option) => (
              <List.Item>
                <Text>{option.months} months</Text>
                <Tag color="blue">x{option.multiplier}</Tag>
              </List.Item>
            )}
          />
        </>
      )}
      {restrictions && (
        <>
          <Divider />
          <Title level={5}>Restrictions</Title>
          <List
            dataSource={Object.entries(restrictions)}
            renderItem={([key, value]) => (
              <List.Item>
                <Text>
                  {key}: {Array.isArray(value) ? value.join(', ') : value}
                </Text>
              </List.Item>
            )}
          />
        </>
      )}
    </Card>
  );
};

export default RateCardViewer;
