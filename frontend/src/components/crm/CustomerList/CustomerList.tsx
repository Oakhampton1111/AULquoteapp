import React, { useState, useEffect } from 'react';
import { Table, Card, Input, Button, Tag, Tooltip, message } from 'antd';
import { SearchOutlined, PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { crmApi, CustomerWithCRMStats } from '../../../services/api/crm';
import { animations } from '../../../styles/animations';

const { Search } = Input;

const ListContainer = styled(Card)`
  margin: 24px;
  ${animations.fadeIn}
`;

const TableActions = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

// Add a comment to trigger the watcher
// Test change for file watcher - 2025-02-25
interface Customer {
  id: number;
  name: string;
  company: string;
  email: string;
  phone: string;
  totalDealValue: number;
  activeDeals: number;
  lastInteraction: string;
  successRate: number;
}

interface CustomerListProps {
  customers: CustomerWithCRMStats[];
  onCustomerSelect: (customer: CustomerWithCRMStats) => void;
}

// Test change for file watcher - 2025-02-25 18:05
// Test change for file watcher - 2025-02-25 18:24
// Test change for file watcher - 2025-02-25 18:25
// Test change for file watcher - 2025-02-25 18:28
export const CustomerList: React.FC<CustomerListProps> = ({ customers, onCustomerSelect }) => {
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    loadCustomers();
  }, [pagination.current, pagination.pageSize]);

  const loadCustomers = async () => {
    setLoading(true);
    try {
      const data = await crmApi.getCustomersWithStats({
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize
      });
      customers = data;
      setPagination(prev => ({ ...prev, total: data.length }));
    } catch (error) {
      message.error('Failed to load customers');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: CustomerWithCRMStats, b: CustomerWithCRMStats) => a.name.localeCompare(b.name),
      render: (text: string, record: CustomerWithCRMStats) => (
        <a onClick={() => navigate(`/crm/customers/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: 'Company',
      dataIndex: 'company',
      key: 'company',
      sorter: (a: CustomerWithCRMStats, b: CustomerWithCRMStats) => a.company.localeCompare(b.company),
    },
    {
      title: 'Total Deal Value',
      dataIndex: 'totalDealValue',
      key: 'totalDealValue',
      sorter: (a: CustomerWithCRMStats, b: CustomerWithCRMStats) => a.totalDealValue - b.totalDealValue,
      render: (value: number) => `$${value.toLocaleString()}`,
    },
    {
      title: 'Active Deals',
      dataIndex: 'activeDeals',
      key: 'activeDeals',
      sorter: (a: CustomerWithCRMStats, b: CustomerWithCRMStats) => a.activeDeals - b.activeDeals,
    },
    {
      title: 'Last Interaction',
      dataIndex: 'lastInteraction',
      key: 'lastInteraction',
      sorter: (a: CustomerWithCRMStats, b: CustomerWithCRMStats) =>
        new Date(a.lastInteraction || 0).getTime() - new Date(b.lastInteraction || 0).getTime(),
      render: (date: string | null) => date ? new Date(date).toLocaleDateString() : 'Never',
    },
    {
      title: 'Success Rate',
      dataIndex: 'successRate',
      key: 'successRate',
      sorter: (a: CustomerWithCRMStats, b: CustomerWithCRMStats) => a.successRate - b.successRate,
      render: (rate: number) => {
        const color = rate >= 70 ? 'green' : rate >= 40 ? 'orange' : 'red';
        return <Tag color={color}>{rate.toFixed(1)}%</Tag>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: CustomerWithCRMStats) => (
        <div>
          <Tooltip title="View Details">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/crm/customers/${record.id}`)}
            />
          </Tooltip>
        </div>
      ),
    },
  ];

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.name.toLowerCase().includes(searchText.toLowerCase()) ||
      customer.company.toLowerCase().includes(searchText.toLowerCase())
  );

  return (
    <ListContainer>
      <TableActions>
        <Search
          placeholder="Search customers..."
          allowClear
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 300 }}
        />
        <Button type="primary" icon={<PlusOutlined />}>
          Add Customer
        </Button>
      </TableActions>

      <Table
        dataSource={filteredCustomers}
        columns={columns}
        loading={loading}
        rowKey="id"
        pagination={{
          ...pagination,
          onChange: (page, pageSize) => {
            setPagination(prev => ({ ...prev, current: page, pageSize }));
          },
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} customers`,
        }}
      />
    </ListContainer>
  );
};
