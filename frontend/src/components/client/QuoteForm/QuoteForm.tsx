import React from 'react';
import { Form, Input, Select, InputNumber, Button, Card, Space, DatePicker } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import { useMutation, useQuery } from '@tanstack/react-query';
import { createQuote } from '../../../services/api/quotes';
import { fetchRateCards } from '../../../services/api/rateCards';

const { Option } = Select;

const StyledCard = styled(Card)`
  max-width: 800px;
  margin: 0 auto;
`;

const StyledSpace = styled(Space)`
  display: flex;
  margin-bottom: 8px;
`;

interface QuoteFormData {
  clientName: string;
  email: string;
  phone: string;
  vehicleDetails: {
    make: string;
    model: string;
    year: number;
    vin: string;
  };
  coverage: {
    type: string;
    duration: number;
    startDate: Date;
  };
  additionalOptions: {
    name: string;
    cost: number;
  }[];
}

export const QuoteForm: React.FC = () => {
  const [form] = Form.useForm();
  
  const { data: rateCards } = useQuery(['rateCards'], fetchRateCards);
  
  const createQuoteMutation = useMutation(createQuote, {
    onSuccess: () => {
      form.resetFields();
      // Show success message
    },
  });

  const onFinish = (values: QuoteFormData) => {
    createQuoteMutation.mutate(values);
  };

  return (
    <StyledCard title="Create New Quote">
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{
          additionalOptions: [{ name: '', cost: 0 }],
        }}
      >
        {/* Client Information */}
        <Card title="Client Information" type="inner" style={{ marginBottom: 24 }}>
          <Form.Item
            name="clientName"
            label="Full Name"
            rules={[{ required: true, message: 'Please enter client name' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please enter email' },
              { type: 'email', message: 'Please enter a valid email' },
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="phone"
            label="Phone"
            rules={[{ required: true, message: 'Please enter phone number' }]}
          >
            <Input />
          </Form.Item>
        </Card>

        {/* Vehicle Details */}
        <Card title="Vehicle Details" type="inner" style={{ marginBottom: 24 }}>
          <Form.Item
            name={['vehicleDetails', 'make']}
            label="Make"
            rules={[{ required: true, message: 'Please enter vehicle make' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name={['vehicleDetails', 'model']}
            label="Model"
            rules={[{ required: true, message: 'Please enter vehicle model' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name={['vehicleDetails', 'year']}
            label="Year"
            rules={[{ required: true, message: 'Please enter vehicle year' }]}
          >
            <InputNumber style={{ width: '100%' }} min={1900} max={2025} />
          </Form.Item>

          <Form.Item
            name={['vehicleDetails', 'vin']}
            label="VIN"
            rules={[{ required: true, message: 'Please enter VIN' }]}
          >
            <Input />
          </Form.Item>
        </Card>

        {/* Coverage Details */}
        <Card title="Coverage Details" type="inner" style={{ marginBottom: 24 }}>
          <Form.Item
            name={['coverage', 'type']}
            label="Coverage Type"
            rules={[{ required: true, message: 'Please select coverage type' }]}
          >
            <Select>
              {rateCards?.map((card: any) => (
                <Option key={card.id} value={card.id}>
                  {card.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name={['coverage', 'duration']}
            label="Duration (months)"
            rules={[{ required: true, message: 'Please select duration' }]}
          >
            <Select>
              <Option value={12}>12 Months</Option>
              <Option value={24}>24 Months</Option>
              <Option value={36}>36 Months</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name={['coverage', 'startDate']}
            label="Start Date"
            rules={[{ required: true, message: 'Please select start date' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Card>

        {/* Additional Options */}
        <Card title="Additional Options" type="inner" style={{ marginBottom: 24 }}>
          <Form.List name="additionalOptions">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <StyledSpace key={key} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'name']}
                      rules={[{ required: true, message: 'Missing option name' }]}
                    >
                      <Input placeholder="Option Name" />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'cost']}
                      rules={[{ required: true, message: 'Missing cost' }]}
                    >
                      <InputNumber
                        placeholder="Cost"
                        formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                        parser={value => value!.replace(/\$\s?|(,*)/g, '')}
                      />
                    </Form.Item>
                    <MinusCircleOutlined onClick={() => remove(name)} />
                  </StyledSpace>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    Add Option
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        </Card>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={createQuoteMutation.isLoading}>
            Create Quote
          </Button>
        </Form.Item>
      </Form>
    </StyledCard>
  );
};
