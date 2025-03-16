import React, { useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  Button,
  message,
} from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { generateQuote } from '../../services/api/quotes';
import { useCustomers } from '../../hooks/useCustomers';

const { TextArea } = Input;

interface QuoteGeneratorProps {
  visible: boolean;
  onClose: () => void;
}

export const QuoteGenerator: React.FC<QuoteGeneratorProps> = ({
  visible,
  onClose,
}) => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const { data: customers } = useCustomers();
  const [isGenerating, setIsGenerating] = useState(false);

  const generateMutation = useMutation(generateQuote, {
    onSuccess: () => {
      message.success('Quote generated and sent to customer');
      queryClient.invalidateQueries(['quotes']);
      form.resetFields();
      onClose();
    },
    onError: (error: any) => {
      message.error(error.message || 'Failed to generate quote');
    },
    onSettled: () => {
      setIsGenerating(false);
    },
  });

  const handleSubmit = async (values: any) => {
    setIsGenerating(true);
    generateMutation.mutate(values);
  };

  return (
    <Modal
      title="Generate Quote"
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          name="customerId"
          label="Customer"
          rules={[{ required: true, message: 'Please select a customer' }]}
        >
          <Select
            placeholder="Select customer"
            showSearch
            optionFilterProp="children"
          >
            {customers?.map((customer) => (
              <Select.Option key={customer.id} value={customer.id}>
                {customer.name}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="requirements"
          label="Service Requirements"
          rules={[{ required: true, message: 'Please enter service requirements' }]}
        >
          <TextArea
            rows={4}
            placeholder="Describe the service requirements in detail..."
          />
        </Form.Item>

        <Form.Item className="mb-0 text-right">
          <Button onClick={onClose} style={{ marginRight: 8 }}>
            Cancel
          </Button>
          <Button
            type="primary"
            htmlType="submit"
            loading={isGenerating}
          >
            Generate Quote
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};
