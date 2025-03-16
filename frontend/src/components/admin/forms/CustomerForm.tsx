import React from 'react';
import { Form, Input, Button, Space } from 'antd';
import { Customer } from '../../../types/customer';

interface CustomerFormProps {
  initialValues?: Partial<Customer>;
  onSubmit: (values: Partial<Customer>) => void;
  onCancel: () => void;
}

export const CustomerForm: React.FC<CustomerFormProps> = ({
  initialValues,
  onSubmit,
  onCancel,
}) => {
  const [form] = Form.useForm();

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
      onFinish={onSubmit}
    >
      <Form.Item
        name="name"
        label="Name"
        rules={[{ required: true, message: 'Please enter customer name' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="email"
        label="Email"
        rules={[
          { required: true, message: 'Please enter customer email' },
          { type: 'email', message: 'Please enter a valid email' },
        ]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="phone"
        label="Phone"
        rules={[
          { pattern: /^\+?[\d\s-]+$/, message: 'Please enter a valid phone number' },
        ]}
      >
        <Input />
      </Form.Item>

      <Form.Item className="mb-0">
        <Space>
          <Button onClick={onCancel}>
            Cancel
          </Button>
          <Button type="primary" htmlType="submit">
            {initialValues ? 'Update' : 'Create'}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};
