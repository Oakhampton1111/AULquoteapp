import React from 'react';
import { Form, Input, Select, InputNumber, Button, Space, DatePicker } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import { Quote } from '../../types/quote';
import { useRateCards } from '../../hooks/useRateCards';
import { useCustomers } from '../../hooks/useCustomers';

const { Option } = Select;
const { TextArea } = Input;

const StyledSpace = styled(Space)`
  display: flex;
  margin-bottom: 8px;
`;

interface QuoteFormProps {
  initialValues?: Partial<Quote>;
  onSubmit: (values: any) => void;
  onCancel: () => void;
  mode?: 'create' | 'generate' | 'edit';
}

export const QuoteForm: React.FC<QuoteFormProps> = ({
  initialValues,
  onSubmit,
  onCancel,
  mode = 'create',
}) => {
  const [form] = Form.useForm();
  const { data: rateCards, isLoading: isLoadingRateCards } = useRateCards();
  const { data: customers, isLoading: isLoadingCustomers } = useCustomers();

  const handleSubmit = (values: any) => {
    const formattedValues = {
      ...values,
      validFrom: values.validFrom?.toISOString(),
      validTo: values.validTo?.toISOString(),
      items: values.items?.map((item: any) => ({
        ...item,
        rateCard: rateCards?.find(rc => rc.id === item.rateCardId),
      })),
    };
    onSubmit(formattedValues);
  };

  const isGenerateMode = mode === 'generate';

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
      onFinish={handleSubmit}
    >
      <Form.Item
        name="customerId"
        label="Customer"
        rules={[{ required: true, message: 'Please select a customer' }]}
      >
        <Select
          loading={isLoadingCustomers}
          placeholder="Select customer"
        >
          {customers?.map(customer => (
            <Option key={customer.id} value={customer.id}>
              {customer.name}
            </Option>
          ))}
        </Select>
      </Form.Item>

      {isGenerateMode ? (
        <Form.Item
          name="requirements"
          label="Requirements"
          rules={[{ required: true, message: 'Please enter requirements' }]}
        >
          <TextArea
            rows={4}
            placeholder="Enter detailed requirements for AI quote generation"
          />
        </Form.Item>
      ) : (
        <>
          <Form.List name="items">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'rateCardId']}
                      rules={[{ required: true, message: 'Select rate card' }]}
                    >
                      <Select
                        loading={isLoadingRateCards}
                        placeholder="Select rate card"
                        style={{ width: 200 }}
                      >
                        {rateCards?.map(rateCard => (
                          <Option key={rateCard.id} value={rateCard.id}>
                            {rateCard.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>

                    <Form.Item
                      {...restField}
                      name={[name, 'quantity']}
                      rules={[{ required: true, message: 'Enter quantity' }]}
                    >
                      <InputNumber min={1} placeholder="Quantity" />
                    </Form.Item>

                    <MinusCircleOutlined onClick={() => remove(name)} />
                  </Space>
                ))}

                <Form.Item>
                  <Button
                    type="dashed"
                    onClick={() => add()}
                    block
                    icon={<PlusOutlined />}
                  >
                    Add Item
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>

          <Form.Item
            name="validFrom"
            label="Valid From"
            rules={[{ required: true, message: 'Select start date' }]}
          >
            <DatePicker />
          </Form.Item>

          <Form.Item
            name="validTo"
            label="Valid To"
            rules={[{ required: true, message: 'Select end date' }]}
          >
            <DatePicker />
          </Form.Item>

          <Form.Item
            name="notes"
            label="Notes"
          >
            <TextArea rows={4} />
          </Form.Item>
        </>
      )}

      <Form.Item className="mb-0">
        <Space>
          <Button onClick={onCancel}>
            Cancel
          </Button>
          <Button type="primary" htmlType="submit">
            {mode === 'edit' ? 'Update' : mode === 'generate' ? 'Generate' : 'Create'} Quote
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};
