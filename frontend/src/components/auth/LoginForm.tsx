import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import { useLogin, useResetPassword } from '../../hooks/useAuth';
import { useLocation, useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

const StyledCard = styled(Card)`
  max-width: 400px;
  width: 100%;
  margin: 2rem auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const StyledSpace = styled(Space)`
  width: 100%;
  justify-content: center;
`;

interface LoginFormData {
  email: string;
  password: string;
}

export const LoginForm: React.FC = () => {
  const [form] = Form.useForm();
  const login = useLogin();
  const resetPassword = useResetPassword();
  const [isResetting, setIsResetting] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (values: LoginFormData) => {
    await login.mutateAsync(values);
    navigate(from, { replace: true });
  };

  const handleResetPassword = async (values: { email: string }) => {
    await resetPassword.mutateAsync(values.email);
    setIsResetting(false);
    form.resetFields();
  };

  return (
    <StyledCard>
      {!isResetting ? (
        <>
          <Title level={3} style={{ textAlign: 'center', marginBottom: '2rem' }}>
            Welcome Back
          </Title>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            requiredMark={false}
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: 'Please enter your email' },
                { type: 'email', message: 'Please enter a valid email' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Email"
                size="large"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Please enter your password' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                size="large"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                block
                loading={login.isLoading}
              >
                Log In
              </Button>
            </Form.Item>
          </Form>

          <Divider />

          <StyledSpace direction="vertical" size="small">
            <Button
              type="link"
              onClick={() => setIsResetting(true)}
            >
              Forgot Password?
            </Button>
          </StyledSpace>
        </>
      ) : (
        <>
          <Title level={3} style={{ textAlign: 'center', marginBottom: '2rem' }}>
            Reset Password
          </Title>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleResetPassword}
            requiredMark={false}
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: 'Please enter your email' },
                { type: 'email', message: 'Please enter a valid email' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Email"
                size="large"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                block
                loading={resetPassword.isLoading}
              >
                Reset Password
              </Button>
            </Form.Item>
          </Form>

          <Divider />

          <StyledSpace direction="vertical" size="small">
            <Button
              type="link"
              onClick={() => setIsResetting(false)}
            >
              Back to Login
            </Button>
          </StyledSpace>
        </>
      )}
    </StyledCard>
  );
};
