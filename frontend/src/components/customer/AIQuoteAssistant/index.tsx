import React, { useState, useEffect } from 'react';
import { Card, Typography, Input, Button, List, Avatar, Spin, Alert, Space } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import { useChat } from '../../../hooks/useChat';
import { Message } from '../../../types/chat';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

export const AIQuoteAssistant: React.FC = () => {
  const { messages, isLoading, isTyping, error, sendMessage, clearMessages } = useChat();
  const [inputValue, setInputValue] = useState('');

  // Handle sending message
  const handleSendMessage = () => {
    if (inputValue.trim()) {
      sendMessage(inputValue);
      setInputValue('');
    }
  };

  // Send initial greeting if no messages are present
  useEffect(() => {
    if (messages.length === 0) {
      sendMessage("Hello! How can I help you with your quote today?");
    }
  }, [messages.length, sendMessage]);

  return (
    <Card>
      <Title level={2}>AI Quote Assistant</Title>
      <Paragraph>
        Describe your vehicle and storage needs, and our AI assistant will help you find the best coverage options.
      </Paragraph>
      
      <List
        style={{ minHeight: '300px', maxHeight: '400px', overflowY: 'auto', marginBottom: '16px', border: '1px solid #f0f0f0', padding: '16px' }}
        dataSource={messages}
        renderItem={(item: Message) => (
          <List.Item
            style={{
              textAlign: item.role === 'user' ? 'right' : 'left',
              justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <List.Item.Meta
              avatar={item.role === 'user' ? <Avatar icon={<UserOutlined />} /> : <Avatar icon={<RobotOutlined />} />}
              title={item.role === 'user' ? 'You' : 'Assistant'}
              description={item.content}
              style={{ 
                display: 'inline-block',
                padding: '8px 12px',
                borderRadius: '10px',
                backgroundColor: item.role === 'user' ? '#e6f7ff' : '#f6f6f6',
                maxWidth: '70%',
              }}
            />
            <div style={{ fontSize: '0.75em', color: '#888', marginTop: '4px', display: 'block', width: '100%' }}>
              {new Date(item.timestamp).toLocaleTimeString()}
            </div>
          </List.Item>
        )}
      />

      {isTyping && <Spin tip="Assistant is typing..." style={{ display: 'block', marginBottom: '8px' }} />}
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: '8px' }} />}

      <Space direction="vertical" style={{ width: '100%' }}>
        <TextArea 
          rows={3} 
          placeholder="Type your message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
        />
        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
          {messages.length > 0 && (
            <Button onClick={clearMessages} loading={isLoading}>
              Clear Chat
            </Button>
          )}
          <Button type="primary" onClick={handleSendMessage} loading={isLoading || isTyping}>
            Send
          </Button>
        </Space>
      </Space>
    </Card>
  );
};

export default AIQuoteAssistant;
