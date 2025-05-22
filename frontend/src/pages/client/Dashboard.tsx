import React, { useState } from 'react';
import {
  Layout,
  Row,
  Col,
  Card,
  Tabs,
  Badge,
  Space,
  Button,
  Drawer,
  Alert
} from 'antd';
import {
  RobotOutlined,
  TableOutlined,
  HistoryOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { AIQuoteAssistant } from '../../components/customer/AIQuoteAssistant';
import { RateCardViewer } from '../../components/customer/RateCardViewer';
import { QuoteHistory } from '../../components/customer/QuoteHistory';
import { useQuotes } from '../../hooks/useQuotes';
import { useRateCards } from '../../hooks/useRateCards';

const { Content } = Layout;
const { TabPane } = Tabs;

export const CustomerDashboard: React.FC = () => {
  const [showRateCard, setShowRateCard] = useState(false);
  const { data: quotes = [], isLoading: quotesLoading } = useQuotes();
  const { data: rateCards = [], isLoading: rateCardLoading } = useRateCards();
  const currentRateCard =
    rateCards.find(rc => rc.isActive) || rateCards[0];
  
  // Group quotes by status
  const quotesByStatus = {
    current: quotes?.filter(q => q.status === 'active'),
    pending: quotes?.filter(q => q.status === 'pending'),
    approved: quotes?.filter(q => q.status === 'approved'),
    rejected: quotes?.filter(q => q.status === 'rejected'),
    expired: quotes?.filter(q => q.status === 'expired')
  };
  
  return (
    <Layout className="customer-dashboard">
      <Content style={{ padding: '24px', minHeight: '100vh' }}>
        <Row gutter={[24, 24]}>
          {/* Left Column - AI Assistant */}
          <Col xs={24} lg={14}>
            <Card
              title={
                <Space>
                  <RobotOutlined />
                  <span>AI Quote Assistant</span>
                </Space>
              }
              extra={
                <Button
                  type="link"
                  icon={<TableOutlined />}
                  onClick={() => setShowRateCard(true)}
                >
                  View Rate Card
                </Button>
              }
              style={{ height: 'calc(100vh - 48px)' }}
              bodyStyle={{ height: 'calc(100% - 57px)', padding: 0 }}
            >
              <AIQuoteAssistant />
            </Card>
          </Col>
          
          {/* Right Column - Quote History */}
          <Col xs={24} lg={10}>
            <Card
              title={
                <Space>
                  <HistoryOutlined />
                  <span>Quote History</span>
                </Space>
              }
              style={{ height: 'calc(100vh - 48px)' }}
              bodyStyle={{ height: 'calc(100% - 57px)', padding: 0 }}
            >
              <Tabs defaultActiveKey="current">
                <TabPane
                  tab={
                    <Badge count={quotesByStatus.current?.length || 0}>
                      Current
                    </Badge>
                  }
                  key="current"
                >
                  <QuoteHistory
                    quotes={quotesByStatus.current}
                    loading={quotesLoading}
                    emptyText="No current quotes"
                  />
                </TabPane>
                
                <TabPane
                  tab={
                    <Badge count={quotesByStatus.pending?.length || 0}>
                      Pending
                    </Badge>
                  }
                  key="pending"
                >
                  <QuoteHistory
                    quotes={quotesByStatus.pending}
                    loading={quotesLoading}
                    emptyText="No pending quotes"
                  />
                </TabPane>
                
                <TabPane
                  tab={
                    <Badge count={quotesByStatus.approved?.length || 0}>
                      Approved
                    </Badge>
                  }
                  key="approved"
                >
                  <QuoteHistory
                    quotes={quotesByStatus.approved}
                    loading={quotesLoading}
                    emptyText="No approved quotes"
                  />
                </TabPane>
                
                <TabPane
                  tab={
                    <Badge count={quotesByStatus.rejected?.length || 0}>
                      Rejected
                    </Badge>
                  }
                  key="rejected"
                >
                  <QuoteHistory
                    quotes={quotesByStatus.rejected}
                    loading={quotesLoading}
                    emptyText="No rejected quotes"
                  />
                </TabPane>
                
                <TabPane
                  tab={
                    <Badge count={quotesByStatus.expired?.length || 0}>
                      Expired
                    </Badge>
                  }
                  key="expired"
                >
                  <QuoteHistory
                    quotes={quotesByStatus.expired}
                    loading={quotesLoading}
                    emptyText="No expired quotes"
                  />
                </TabPane>
              </Tabs>
            </Card>
          </Col>
        </Row>
        
        {/* Rate Card Drawer */}
        <Drawer
          title={
            <Space>
              <FileTextOutlined />
              <span>Current Rate Card</span>
            </Space>
          }
          placement="right"
          width={720}
          onClose={() => setShowRateCard(false)}
          open={showRateCard}
        >
          {rateCardLoading ? (
            <Alert
              message="Loading rate card..."
              type="info"
              showIcon
            />
          ) : currentRateCard ? (
            <RateCardViewer rateCard={currentRateCard} />
          ) : (
            <Alert
              message="No rate card available"
              type="warning"
              showIcon
            />
          )}
        </Drawer>
      </Content>
    </Layout>
  );
};
