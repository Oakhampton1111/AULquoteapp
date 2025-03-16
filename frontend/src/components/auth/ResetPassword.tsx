import React from 'react';
import { Form, Input, Button, Card, Typography } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import { useUpdatePassword } from '../../hooks/useAuth';
import { useNavigate, useSearchParams } from 'react-router-dom';

const { Title, Text } = Typography;

const StyledCard = styled(Card)`
  max-width: 400px;
  width: 100%;
  margin: 2rem auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

interface ResetPasswordFormData {
  password: string;
  confirmPassword: string;
}

export const ResetPassword: React.FC = () => {
  const [form] = Form.useForm();
  const updatePassword = useUpdatePassword();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const handleSubmit = async (values: ResetPasswordFormData) => {
    if (!token) {
      return;
    }

    await updatePassword.mutateAsync({
      token,
      password: values.password,
    });
    
    navigate('/login');
  };

  if (!token) {
    return (
      <StyledCard>
        <Title level={3} style={{ textAlign: 'center' }}>
          Invalid Reset Link
        </Title>
        <Text>
          This password reset link is invalid or has expired. Please request a new password reset.
        </Text>
        <Button
          type="primary"
          block
          style={{ marginTop: '1rem' }}
          onClick={() => navigate('/login')}
        >
          Back to Login
        </Button>
      </StyledCard>
    );
  }

  return (
    <StyledCard>
      <Title level={3} style={{ textAlign: 'center', marginBottom: '2rem' }}>
        Reset Your Password
      </Title>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        requiredMark={false}
      >
        <Form.Item
          name="password"
          rules={[
            { required: true, message: 'Please enter your new password' },
            { min: 8, message: 'Password must be at least 8 characters' },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="New Password"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          dependencies={['password']}
          rules={[
            { required: true, message: 'Please confirm your password' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('Passwords do not match'));
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Confirm Password"
            size="large"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            block
            loading={updatePassword.isLoading}
          >
            Reset Password
          </Button>
        </Form.Item>
      </Form>
    </StyledCard>
  );
};
