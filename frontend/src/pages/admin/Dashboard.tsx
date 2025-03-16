import React, { useState } from 'react';
import { Card, Row, Col, Statistic, Tabs, Button } from 'antd';
import {
  UserOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardStats } from '../../services/api/admin';
import styled from 'styled-components';
import { QuoteList } from '../../components/admin/QuoteList';
import { CustomerManager } from '../../components/admin/CustomerManager';
import { RateManager } from '../../components/admin/RateManager';
import { QuoteGenerator } from '../../components/admin/QuoteGenerator';

const { TabPane } = Tabs;

const StyledCard = styled(Card)`
  margin-bottom: 24px;
`;

const ActionButton = styled(Button)`
  margin-left: 8px;
`;

export const AdminDashboard: React.FC = () => {
  const [showQuoteGenerator, setShowQuoteGenerator] = useState(false);
  const { data: stats, isLoading } = useQuery(['adminStats'], fetchDashboardStats);

  const handleGenerateQuote = () => {
    setShowQuoteGenerator(true);
  };

  return (
    <div>
      {/* Stats Overview */}
      <Row gutter={24} className="mb-6">
        <Col span={6}>
          <StyledCard>
            <Statistic
              title="Total Quotes"
              value={stats?.totalQuotes || 0}
              prefix={<FileTextOutlined />}
            />
          </StyledCard>
        </Col>
        <Col span={6}>
          <StyledCard>
            <Statistic
              title="Active Customers"
              value={stats?.activeCustomers || 0}
              prefix={<UserOutlined />}
            />
          </StyledCard>
        </Col>
        <Col span={6}>
          <StyledCard>
            <Statistic
              title="Pending Quotes"
              value={stats?.pendingQuotes || 0}
              prefix={<ClockCircleOutlined />}
            />
          </StyledCard>
        </Col>
        <Col span={6}>
          <StyledCard>
            <Statistic
              title="Approved Quotes"
              value={stats?.approvedQuotes || 0}
              prefix={<CheckCircleOutlined />}
            />
          </StyledCard>
        </Col>
      </Row>

      {/* Main Content */}
      <Card>
        <div className="mb-4">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleGenerateQuote}
          >
            Generate Quote
          </Button>
        </div>

        <Tabs defaultActiveKey="quotes">
          <TabPane tab="Quotes" key="quotes">
            <QuoteList />
          </TabPane>
          <TabPane tab="Customers" key="customers">
            <CustomerManager />
          </TabPane>
          <TabPane tab="Rate Cards" key="rates">
            <RateManager />
          </TabPane>
        </Tabs>
      </Card>

      {/* Quote Generator Modal */}
      <QuoteGenerator
        visible={showQuoteGenerator}
        onClose={() => setShowQuoteGenerator(false)}
      />
    </div>
  );
};
