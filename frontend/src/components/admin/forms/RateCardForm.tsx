import React from 'react';
import { Form, Input, InputNumber, DatePicker, Button, Space } from 'antd';
import { RateCard } from '../../../types/rateCard';
import dayjs from 'dayjs';

interface RateCardFormProps {
  initialValues?: Partial<RateCard>;
  onSubmit: (values: Partial<RateCard>) => void;
  onCancel: () => void;
}

export const RateCardForm: React.FC<RateCardFormProps> = ({
  initialValues,
  onSubmit,
  onCancel,
}) => {
  const [form] = Form.useForm();

  const handleSubmit = (values: any) => {
    // Convert dayjs objects to ISO strings
    const formattedValues = {
      ...values,
      effectiveFrom: values.effectiveFrom?.toISOString(),
      effectiveTo: values.effectiveTo?.toISOString(),
    };
    onSubmit(formattedValues);
  };

  // Convert ISO strings to dayjs objects for form
  const formInitialValues = initialValues
    ? {
        ...initialValues,
        effectiveFrom: initialValues.effectiveFrom ? dayjs(initialValues.effectiveFrom) : undefined,
        effectiveTo: initialValues.effectiveTo ? dayjs(initialValues.effectiveTo) : undefined,
      }
    : undefined;

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={formInitialValues}
      onFinish={handleSubmit}
    >
      <Form.Item
        name="name"
        label="Rate Card Name"
        rules={[{ required: true, message: 'Please enter rate card name' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="description"
        label="Description"
        rules={[{ required: true, message: 'Please enter description' }]}
      >
        <Input.TextArea rows={3} />
      </Form.Item>

      <Form.Item
        name="baseRate"
        label="Base Rate"
        rules={[{ required: true, message: 'Please enter base rate' }]}
      >
        <InputNumber
          min={0}
          precision={2}
          style={{ width: '100%' }}
          formatter={(value) => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
          parser={(value) => value!.replace(/\$\s?|(,*)/g, '')}
        />
      </Form.Item>

      <Form.Item
        name="effectiveFrom"
        label="Effective From"
        rules={[{ required: true, message: 'Please select start date' }]}
      >
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item
        name="effectiveTo"
        label="Effective To"
        rules={[{ required: true, message: 'Please select end date' }]}
      >
        <DatePicker style={{ width: '100%' }} />
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
