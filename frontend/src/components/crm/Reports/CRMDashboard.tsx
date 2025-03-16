import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Progress } from 'antd';
import styled from 'styled-components';
import { appTheme } from '../../../styles/theme';
import { animations } from '../../../styles/animations';
import { crmApi, PipelineStats } from '../../../services/api/crm';
import { DealStage } from '../../../services/api/types';

const { Title, Text } = Typography;

const DashboardContainer = styled.div`
  padding: 1rem;
  ${animations.fadeIn}
`;

const StatsCard = styled(Card)`
  margin-bottom: 1rem;
  text-align: center;
  background: ${appTheme.token.colorBgContainer};
`;

const StageProgress = styled(Progress)`
  .ant-progress-text {
    color: ${appTheme.token.colorTextSecondary};
  }
`;

export const CRMDashboard: React.FC = () => {
  const [stats, setStats] = useState<PipelineStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const pipelineStats = await crmApi.getPipelineStats();
      setStats(pipelineStats);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!stats) {
    return <DashboardContainer>Loading...</DashboardContainer>;
  }

  return (
    <DashboardContainer>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <StatsCard>
            <Title level={3}>{stats.totalDeals}</Title>
            <Text type="secondary">Total Deals</Text>
          </StatsCard>
        </Col>
        <Col span={6}>
          <StatsCard>
            <Title level={3}>${stats.totalValue.toLocaleString()}</Title>
            <Text type="secondary">Pipeline Value</Text>
          </StatsCard>
        </Col>
        <Col span={6}>
          <StatsCard>
            <Title level={3}>{stats.winRate.toFixed(1)}%</Title>
            <Text type="secondary">Win Rate</Text>
          </StatsCard>
        </Col>
      </Row>

      <Card title="Pipeline Stages" style={{ marginTop: '1rem' }}>
        {stats.stages.map(stage => {
          const percentage = (stage.count / stats.totalDeals) * 100;
          return (
            <div key={stage.stage} style={{ marginBottom: '1rem' }}>
              <Text>{stage.stage}</Text>
              <Row>
                <Col span={16}>
                  <StageProgress
                    percent={percentage}
                    status="active"
                    showInfo={false}
                  />
                </Col>
                <Col span={4} style={{ textAlign: 'right' }}>
                  <Text>{stage.count} deals</Text>
                </Col>
                <Col span={4} style={{ textAlign: 'right' }}>
                  <Text>${stage.value.toLocaleString()}</Text>
                </Col>
              </Row>
            </div>
          );
        })}
      </Card>
    </DashboardContainer>
  );
};
