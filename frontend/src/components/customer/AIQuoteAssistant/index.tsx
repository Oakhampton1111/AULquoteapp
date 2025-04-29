import React from 'react';
import { Card, Typography, Input, Button, Space } from 'antd';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

export const AIQuoteAssistant: React.FC = () => {
  return (
    <Card>
      <Title level={2}>AI Quote Assistant</Title>
      <Paragraph>
        Describe your vehicle and storage needs, and our AI assistant will help you find the best coverage options.
      </Paragraph>
      <Space direction="vertical" style={{ width: '100%' }}>
        <TextArea 
          rows={4} 
          placeholder="E.g., I need coverage for my 2020 Toyota Camry that I'll be storing for 6 months while I'm overseas..."
        />
        <Button type="primary">Get Recommendations</Button>
      </Space>
    </Card>
  );
};

export default AIQuoteAssistant;
