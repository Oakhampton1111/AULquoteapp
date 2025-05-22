import React, { useEffect, useState } from 'react';
import { Card, Tabs, Timeline, List, Typography, Tag, message } from 'antd';
import styled from 'styled-components';
import { appTheme } from '../../../styles/theme';
import { animations } from '../../../styles/animations';
import { crmApi, Deal, Interaction, CustomerCRMStats } from '../../../services/api/crm';
import { InteractionType } from '../../../services/api/types';

const { Title, Text } = Typography;

interface CustomerProfileProps {
  customerId: number;
  name: string;
  company: string;
}

const ProfileContainer = styled(Card)`
  margin: 1rem;
  ${animations.fadeIn}
`;

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
`;

const StatCard = styled(Card)`
  text-align: center;
  background: ${appTheme.token.colorBgContainer};
`;

const InteractionTimeline = styled(Timeline)`
  margin-top: 1rem;
`;

const DealsList = styled(List)`
  .ant-list-item {
    transition: background-color 0.3s;
    &:hover {
      background-color: ${appTheme.token.colorBgLayout};
    }
  }
`;

export const CustomerProfile: React.FC<CustomerProfileProps> = ({
  customerId,
  name,
  company,
}) => {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [stats, setStats] = useState<CustomerCRMStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomerData();
  }, [customerId]);

  const loadCustomerData = async () => {
    setLoading(true);
    try {
      const [customerStats, customerInteractions, customerDeals] = await Promise.all([
        crmApi.getCustomerCRMStats(customerId),
        crmApi.getCustomerInteractions(customerId),
        crmApi.getCustomerDeals(customerId)
      ]);
      
      setStats(customerStats);
      setInteractions(customerInteractions);
      setDeals(customerDeals);
    } catch (error) {
      message.error('Failed to load customer data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProfileContainer loading={loading}>
      <Title level={2}>{name}</Title>
      <Text type="secondary">{company}</Text>

      {stats && (
        <StatsContainer>
          <StatCard>
            <Title level={4}>${stats.totalDealValue.toLocaleString()}</Title>
            <Text type="secondary">Total Deal Value</Text>
          </StatCard>
          <StatCard>
            <Title level={4}>${stats.activeDealValue.toLocaleString()}</Title>
            <Text type="secondary">Active Deal Value</Text>
          </StatCard>
          <StatCard>
            <Title level={4}>{stats.activeDeals}</Title>
            <Text type="secondary">Active Deals</Text>
          </StatCard>
          <StatCard>
            <Title level={4}>{stats.successRate.toFixed(1)}%</Title>
            <Text type="secondary">Success Rate</Text>
          </StatCard>
        </StatsContainer>
      )}

      <Tabs
        items={[
          {
            key: '1',
            label: 'Interactions',
            children: (
              <InteractionTimeline>
                {interactions.map(interaction => (
                  <Timeline.Item key={interaction.id}>
                    <Text strong>{interaction.type}</Text>
                    <br />
                    {interaction.description}
                    <br />
                    <Text type="secondary">
                      {new Date(interaction.createdAt).toLocaleDateString()}
                    </Text>
                  </Timeline.Item>
                ))}
              </InteractionTimeline>
            ),
          },
          {
            key: '2',
            label: 'Deals',
            children: (
              <DealsList
                dataSource={deals}
                renderItem={(deal) => (
                  <List.Item>
                    <List.Item.Meta
                      title={deal.title}
                      description={`Last updated: ${new Date(deal.updatedAt).toLocaleDateString()}`}
                    />
                    <div>
                      <Tag color="blue">{deal.stage}</Tag>
                      <div>${deal.value?.toLocaleString() || 0}</div>
                      <div>{deal.probability}% probability</div>
                    </div>
                  </List.Item>
                )}
              />
            ),
          }
        ]}
      />
    </ProfileContainer>
  );
};
