import React, { useState } from 'react';
import { Card, Typography, Input, Button, Space, List, Spin, message } from 'antd';
import { useMutation } from '@tanstack/react-query';
import apiClient from '../../../services/api/client';
import { Message as ChatMessage } from '../../../types/chat';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

export const AIQuoteAssistant: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const sendMessage = useMutation(
    async (content: string) => {
      const response = await apiClient.post('/chat/message', { message: content });
      return response.data as { content: string };
    },
    {
      onSuccess: (data) => {
        setMessages((prev) => [...prev, { role: 'assistant', content: data.content, timestamp: new Date() }]);
      },
      onError: (err: any) => {
        message.error(err.response?.data?.detail || 'Failed to send message');
      },
    }
  );

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', content: input.trim(), timestamp: new Date() }]);
    const current = input;
    setInput('');
    await sendMessage.mutateAsync(current.trim());
  };

  return (
    <Card style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Title level={2}>AI Quote Assistant</Title>
      <Paragraph>
        Describe your vehicle and storage needs, and our AI assistant will help you find the best coverage options.
      </Paragraph>
      <Space direction="vertical" style={{ width: '100%', flex: 1 }}>
        <List
          dataSource={messages}
          renderItem={(item) => (
            <List.Item>
              <Typography.Text strong={item.role === 'user'}>{item.role === 'user' ? 'You: ' : 'AI: '}</Typography.Text>
              <Typography.Text>{item.content}</Typography.Text>
            </List.Item>
          )}
          style={{ flex: 1, overflowY: 'auto' }}
        />
        {sendMessage.isLoading && (
          <div style={{ textAlign: 'center', marginBottom: 8 }}>
            <Spin size="small" />
          </div>
        )}
        <TextArea
          rows={3}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Type your question..."
        />
        <Button type="primary" onClick={handleSend} loading={sendMessage.isLoading}>
          Send
        </Button>
      </Space>
    </Card>
  );
};

export default AIQuoteAssistant;
