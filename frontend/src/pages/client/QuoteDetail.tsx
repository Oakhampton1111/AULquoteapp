import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Button, Space, Modal, Form, InputNumber, Input } from 'antd';
import {
  useQuote,
  useAcceptQuote,
  useNegotiateQuote,
  useUpdateQuoteStatus,
  QuoteNegotiationPayload,
} from '../../hooks/useQuotes';

const { Item } = Descriptions;

export const QuoteDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const quoteId = Number(id);

  const { data: quote, isLoading } = useQuote(quoteId);
  const acceptQuote = useAcceptQuote();
  const updateStatus = useUpdateQuoteStatus();
  const negotiateQuote = useNegotiateQuote();

  const [negotiationVisible, setNegotiationVisible] = useState(false);
  const [form] = Form.useForm<Pick<QuoteNegotiationPayload, 'discount_percentage' | 'reason'>>();

  const handleAccept = async () => {
    await acceptQuote.mutateAsync(quoteId);
    navigate(-1);
  };

  const handleReject = async () => {
    await updateStatus.mutateAsync({ id: quoteId, status: 'rejected' });
    navigate(-1);
  };

  const submitNegotiation = async () => {
    const values = await form.validateFields();
    await negotiateQuote.mutateAsync({ id: quoteId, ...values });
    setNegotiationVisible(false);
  };

  if (isLoading || !quote) {
    return <p>Loading...</p>;
  }

  const statusColor: Record<string, string> = {
    pending: 'gold',
    accepted: 'green',
    rejected: 'red',
    expired: 'gray',
  };

  return (
    <Card title={`Quote #${quote.quote_number}`}>
      <Descriptions bordered column={1} size="small">
        <Item label="Status">
          <Tag color={statusColor[quote.status] || 'default'}>{quote.status.toUpperCase()}</Tag>
        </Item>
        <Item label="Service Type">{quote.service_type}</Item>
        <Item label="Base Price">${quote.base_price.toFixed(2)}</Item>
        <Item label="Handling Fees">${(quote.handling_fees || 0).toFixed(2)}</Item>
        <Item label="Tax Rate">{quote.tax_rate ? `${quote.tax_rate}%` : 'N/A'}</Item>
        <Item label="Discount">{quote.discount ? `${quote.discount}%` : 'N/A'}</Item>
        <Item label="Total Amount">${quote.total_amount.toFixed(2)}</Item>
      </Descriptions>
      <Space style={{ marginTop: 16 }}>
        {quote.status === 'pending' && (
          <>
            <Button type="primary" onClick={handleAccept} loading={acceptQuote.isLoading}>
              Accept Quote
            </Button>
            <Button danger onClick={handleReject} loading={updateStatus.isLoading}>
              Reject Quote
            </Button>
            <Button onClick={() => setNegotiationVisible(true)} loading={negotiateQuote.isLoading}>
              Request Discount
            </Button>
          </>
        )}
      </Space>
      <Modal
        title="Request Discount"
        open={negotiationVisible}
        onCancel={() => setNegotiationVisible(false)}
        onOk={submitNegotiation}
        okText="Submit"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="discount_percentage"
            label="Discount (%)"
            rules={[{ required: true, message: 'Enter discount percentage' }]}
          >
            <InputNumber min={1} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="reason" label="Reason" rules={[{ required: true, message: 'Enter reason' }]}>
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default QuoteDetail;
