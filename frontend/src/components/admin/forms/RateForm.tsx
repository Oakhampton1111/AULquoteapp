import React from 'react';
import { Form, Input, InputNumber, Select, Switch, Button, Space } from 'antd';
import { Rate, RateInput } from '../../../types/rate';

const { Option } = Select;

export interface RateFormProps {
  initialValues?: Partial<Rate>;
  onSubmit: (values: RateInput | Partial<RateInput>) => void;
  onCancel: () => void;
}

export const RateForm: React.FC<RateFormProps> = ({ initialValues, onSubmit, onCancel }) => {
  const [form] = Form.useForm();

  const handleFinish = (values: any) => {
    onSubmit(values);
  };

  return (
    <Form form={form} layout="vertical" initialValues={initialValues} onFinish={handleFinish}>
      <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Enter name' }]}> 
        <Input />
      </Form.Item>
      <Form.Item name="description" label="Description">
        <Input.TextArea rows={2} />
      </Form.Item>
      <Form.Item name="category" label="Category" rules={[{ required: true, message: 'Select category' }]}> 
        <Select>
          <Option value="storage">Storage</Option>
          <Option value="handling">Handling</Option>
          <Option value="additional">Additional</Option>
          <Option value="container">Container</Option>
          <Option value="transport">Transport</Option>
          <Option value="export">Export</Option>
        </Select>
      </Form.Item>
      <Form.Item name="rate" label="Rate" rules={[{ required: true, message: 'Enter rate' }]}> 
        <InputNumber min={0} style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item name="unit" label="Unit" rules={[{ required: true, message: 'Select unit' }]}> 
        <Select>
          <Option value="item">Item</Option>
          <Option value="pallet">Pallet</Option>
          <Option value="box">Box</Option>
          <Option value="container">Container</Option>
          <Option value="kg">Kg</Option>
          <Option value="hour">Hour</Option>
          <Option value="day">Day</Option>
          <Option value="flat">Flat</Option>
        </Select>
      </Form.Item>
      <Form.Item name="is_active" valuePropName="checked" label="Active">
        <Switch />
      </Form.Item>
      <Form.Item>
        <Space>
          <Button onClick={onCancel}>Cancel</Button>
          <Button type="primary" htmlType="submit">
            {initialValues ? 'Update' : 'Create'}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default RateForm;
