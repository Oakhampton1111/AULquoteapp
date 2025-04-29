/**
 * Enhanced Quote Form
 * 
 * An improved version of the QuoteForm component with:
 * - Accessibility improvements
 * - Better form validation
 * - Improved loading states
 * - Enhanced error handling
 * - Responsive design
 * - Performance optimizations
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Form, 
  Input, 
  Select, 
  InputNumber, 
  Button, 
  Card, 
  Space, 
  DatePicker, 
  Divider, 
  Alert, 
  Spin, 
  Typography, 
  Steps, 
  Result,
  Tooltip,
  Skeleton
} from 'antd';
import { 
  PlusOutlined, 
  MinusCircleOutlined, 
  InfoCircleOutlined, 
  CheckCircleOutlined,
  LeftOutlined,
  RightOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import styled, { css } from 'styled-components';
import { useMutation, useQuery } from '@tanstack/react-query';
import { createQuote } from '../../../services/api/quotes';
import { fetchRateCards } from '../../../services/api/rateCards';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useMediaQuery } from '../../../hooks/useMediaQuery';
import { useFormProgress } from '../../../hooks/useFormProgress';
import { QuoteFormData, RateCard } from '../../../types';

const { Option } = Select;
const { Title, Text, Paragraph } = Typography;
const { Step } = Steps;

// Styled components with proper theme integration
const StyledCard = styled(Card)`
  max-width: 800px;
  margin: 0 auto;
  box-shadow: ${props => props.theme.token.boxShadow};
  border-radius: ${props => props.theme.token.borderRadius}px;
`;

const StyledForm = styled(Form)`
  .ant-form-item-label > label {
    font-weight: 500;
  }

  .ant-form-item-explain-error {
    margin-top: 4px;
  }
`;

const StyledSpace = styled(Space)`
  display: flex;
  margin-bottom: 8px;
`;

const StyledSteps = styled(Steps)`
  margin-bottom: 24px;

  @media (max-width: 576px) {
    .ant-steps-item-title {
      font-size: 12px;
    }
  }
`;

const StepContent = styled(motion.div)`
  min-height: 300px;
`;

const FormActions = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
`;

const ErrorMessage = styled(Alert)`
  margin-bottom: 16px;
`;

const SuccessCard = styled(Card)`
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
`;

const FieldHelpText = styled(Text)`
  color: ${props => props.theme.token.colorTextSecondary};
  font-size: 12px;
`;

// Form steps
const formSteps = [
  {
    title: 'Client Info',
    icon: <InfoCircleOutlined />,
  },
  {
    title: 'Vehicle Details',
    icon: <InfoCircleOutlined />,
  },
  {
    title: 'Coverage',
    icon: <InfoCircleOutlined />,
  },
  {
    title: 'Review',
    icon: <InfoCircleOutlined />,
  },
];

/**
 * Enhanced Quote Form Component
 */
export const EnhancedQuoteForm: React.FC = () => {
  // Hooks
  const [form] = Form.useForm<QuoteFormData>();
  const navigate = useNavigate();
  const isMobile = useMediaQuery('(max-width: 576px)');
  const { saveProgress, loadProgress, clearProgress } = useFormProgress('quote-form');
  
  // State
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Partial<QuoteFormData>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  // Queries
  const { 
    data: rateCards, 
    isLoading: isLoadingRateCards, 
    error: rateCardsError 
  } = useQuery(['rateCards'], fetchRateCards, {
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
  });
  
  // Mutations
  const createQuoteMutation = useMutation(createQuote, {
    onSuccess: (data) => {
      setIsSubmitted(true);
      clearProgress();
      // Show success message
    },
    onError: (error: any) => {
      setFormError(error.message || 'Failed to create quote. Please try again.');
      // Log error for analytics
      console.error('Quote creation error:', error);
    },
  });
  
  // Effects
  useEffect(() => {
    // Load saved progress on mount
    const savedProgress = loadProgress();
    if (savedProgress) {
      form.setFieldsValue(savedProgress);
      setFormData(savedProgress);
      
      // Determine which step to start at based on saved data
      if (savedProgress.coverage) {
        setCurrentStep(3); // Review step
      } else if (savedProgress.vehicleDetails) {
        setCurrentStep(2); // Coverage step
      } else if (savedProgress.email) {
        setCurrentStep(1); // Vehicle details step
      }
    }
  }, [form, loadProgress]);
  
  // Save form progress when values change
  const handleValuesChange = (changedValues: any, allValues: any) => {
    setFormData({ ...formData, ...changedValues });
    saveProgress(allValues);
  };
  
  // Memoized filtered rate cards
  const filteredRateCards = useMemo(() => {
    if (!rateCards) return [];
    
    // Filter based on form data if needed
    return rateCards;
  }, [rateCards, formData]);
  
  // Form submission
  const handleFinish = async (values: QuoteFormData) => {
    try {
      setFormError(null);
      await createQuoteMutation.mutateAsync(values);
    } catch (error) {
      // Error is handled by mutation onError
    }
  };
  
  // Step navigation
  const handleNext = async () => {
    try {
      // Validate fields in current step
      let fieldsToValidate: string[] = [];
      
      switch (currentStep) {
        case 0: // Client Info
          fieldsToValidate = ['clientName', 'email', 'phone'];
          break;
        case 1: // Vehicle Details
          fieldsToValidate = [
            'vehicleDetails.make', 
            'vehicleDetails.model', 
            'vehicleDetails.year', 
            'vehicleDetails.vin'
          ];
          break;
        case 2: // Coverage
          fieldsToValidate = [
            'coverage.type', 
            'coverage.duration', 
            'coverage.startDate'
          ];
          break;
      }
      
      await form.validateFields(fieldsToValidate);
      
      // Save current progress
      const currentValues = form.getFieldsValue();
      saveProgress(currentValues);
      setFormData(currentValues);
      
      // Move to next step
      setCurrentStep(currentStep + 1);
    } catch (error) {
      // Validation failed, stay on current step
      console.log('Validation failed:', error);
    }
  };
  
  const handlePrevious = () => {
    setCurrentStep(currentStep - 1);
  };
  
  // Render loading state
  if (isLoadingRateCards) {
    return (
      <StyledCard title="Create New Quote">
        <LoadingContainer>
          <Spin 
            indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} 
            tip="Loading rate information..."
          />
        </LoadingContainer>
      </StyledCard>
    );
  }
  
  // Render error state
  if (rateCardsError) {
    return (
      <StyledCard title="Create New Quote">
        <Alert
          message="Error Loading Data"
          description="We couldn't load the necessary data. Please try again later."
          type="error"
          action={
            <Button type="primary" onClick={() => window.location.reload()}>
              Retry
            </Button>
          }
        />
      </StyledCard>
    );
  }
  
  // Render success state
  if (isSubmitted) {
    return (
      <SuccessCard>
        <Result
          status="success"
          title="Quote Created Successfully!"
          subTitle="Your quote has been submitted and is being processed."
          extra={[
            <Button 
              type="primary" 
              key="dashboard" 
              onClick={() => navigate('/dashboard')}
            >
              Go to Dashboard
            </Button>,
            <Button 
              key="another" 
              onClick={() => {
                form.resetFields();
                setFormData({});
                setIsSubmitted(false);
                setCurrentStep(0);
              }}
            >
              Create Another Quote
            </Button>,
          ]}
        />
      </SuccessCard>
    );
  }
  
  // Render form
  return (
    <StyledCard 
      title={
        <Title level={4} aria-label="Create New Quote Form">
          Create New Quote
        </Title>
      }
    >
      {formError && (
        <ErrorMessage
          message="Error"
          description={formError}
          type="error"
          closable
          onClose={() => setFormError(null)}
        />
      )}
      
      <StyledSteps current={currentStep} responsive={!isMobile}>
        {formSteps.map(step => (
          <Step key={step.title} title={step.title} icon={step.icon} />
        ))}
      </StyledSteps>
      
      <StyledForm
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        onValuesChange={handleValuesChange}
        initialValues={formData}
        requiredMark="optional"
        aria-label="Quote Form"
      >
        <AnimatePresence mode="wait">
          {currentStep === 0 && (
            <StepContent
              key="step-1"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Title level={5}>Client Information</Title>
              <Paragraph>
                Please provide the client's contact information.
              </Paragraph>
              
              <Form.Item
                label="Client Name"
                name="clientName"
                rules={[{ required: true, message: 'Please enter client name' }]}
                extra={<FieldHelpText>Enter the full name of the client</FieldHelpText>}
              >
                <Input 
                  placeholder="John Doe" 
                  maxLength={100}
                  aria-required="true"
                />
              </Form.Item>
              
              <Form.Item
                label="Email"
                name="email"
                rules={[
                  { required: true, message: 'Please enter email address' },
                  { type: 'email', message: 'Please enter a valid email address' }
                ]}
                extra={<FieldHelpText>All quote information will be sent to this email</FieldHelpText>}
              >
                <Input 
                  placeholder="john.doe@example.com" 
                  type="email"
                  aria-required="true"
                />
              </Form.Item>
              
              <Form.Item
                label="Phone"
                name="phone"
                rules={[
                  { required: true, message: 'Please enter phone number' },
                  { pattern: /^[0-9\-\(\)\.+\s]*$/, message: 'Please enter a valid phone number' }
                ]}
                extra={<FieldHelpText>Format: (123) 456-7890</FieldHelpText>}
              >
                <Input 
                  placeholder="(123) 456-7890" 
                  aria-required="true"
                />
              </Form.Item>
            </StepContent>
          )}
          
          {currentStep === 1 && (
            <StepContent
              key="step-2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Title level={5}>Vehicle Details</Title>
              <Paragraph>
                Please provide information about the vehicle.
              </Paragraph>
              
              <Form.Item
                label="Make"
                name={['vehicleDetails', 'make']}
                rules={[{ required: true, message: 'Please enter vehicle make' }]}
              >
                <Input placeholder="Toyota" aria-required="true" />
              </Form.Item>
              
              <Form.Item
                label="Model"
                name={['vehicleDetails', 'model']}
                rules={[{ required: true, message: 'Please enter vehicle model' }]}
              >
                <Input placeholder="Camry" aria-required="true" />
              </Form.Item>
              
              <Form.Item
                label="Year"
                name={['vehicleDetails', 'year']}
                rules={[
                  { required: true, message: 'Please enter vehicle year' },
                  { type: 'number', min: 1900, max: new Date().getFullYear() + 1, message: 'Please enter a valid year' }
                ]}
              >
                <InputNumber 
                  placeholder="2022" 
                  style={{ width: '100%' }} 
                  min={1900} 
                  max={new Date().getFullYear() + 1}
                  aria-required="true"
                />
              </Form.Item>
              
              <Form.Item
                label="VIN"
                name={['vehicleDetails', 'vin']}
                rules={[
                  { required: true, message: 'Please enter vehicle VIN' },
                  { pattern: /^[A-HJ-NPR-Z0-9]{17}$/i, message: 'Please enter a valid 17-character VIN' }
                ]}
                extra={<FieldHelpText>17-character Vehicle Identification Number</FieldHelpText>}
              >
                <Input 
                  placeholder="1HGCM82633A123456" 
                  maxLength={17}
                  aria-required="true"
                />
              </Form.Item>
            </StepContent>
          )}
          
          {currentStep === 2 && (
            <StepContent
              key="step-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Title level={5}>Coverage Details</Title>
              <Paragraph>
                Select the coverage type and duration.
              </Paragraph>
              
              <Form.Item
                label="Coverage Type"
                name={['coverage', 'type']}
                rules={[{ required: true, message: 'Please select coverage type' }]}
              >
                <Select 
                  placeholder="Select coverage type"
                  aria-required="true"
                >
                  {filteredRateCards.map((card: RateCard) => (
                    <Option key={card.id} value={card.name}>
                      {card.name} - ${card.baseRate}/month
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              
              <Form.Item
                label="Duration (months)"
                name={['coverage', 'duration']}
                rules={[
                  { required: true, message: 'Please enter duration' },
                  { type: 'number', min: 1, max: 60, message: 'Duration must be between 1 and 60 months' }
                ]}
              >
                <InputNumber 
                  placeholder="12" 
                  style={{ width: '100%' }} 
                  min={1} 
                  max={60}
                  aria-required="true"
                />
              </Form.Item>
              
              <Form.Item
                label="Start Date"
                name={['coverage', 'startDate']}
                rules={[{ required: true, message: 'Please select start date' }]}
              >
                <DatePicker 
                  style={{ width: '100%' }} 
                  disabledDate={(current) => {
                    // Can't select days before today
                    return current && current < new Date(Date.now() - 24 * 60 * 60 * 1000);
                  }}
                  aria-required="true"
                />
              </Form.Item>
              
              <Divider />
              
              <Form.List name="additionalOptions">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <StyledSpace key={key} align="baseline">
                        <Form.Item
                          {...restField}
                          name={[name, 'name']}
                          rules={[{ required: true, message: 'Missing option name' }]}
                          style={{ marginBottom: 0 }}
                        >
                          <Input placeholder="Option Name" />
                        </Form.Item>
                        <Form.Item
                          {...restField}
                          name={[name, 'cost']}
                          rules={[{ required: true, message: 'Missing cost' }]}
                          style={{ marginBottom: 0 }}
                        >
                          <InputNumber
                            placeholder="Cost"
                            min={0}
                            formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                            parser={value => value!.replace(/\$\s?|(,*)/g, '')}
                          />
                        </Form.Item>
                        <MinusCircleOutlined onClick={() => remove(name)} />
                      </StyledSpace>
                    ))}
                    <Form.Item>
                      <Button
                        type="dashed"
                        onClick={() => add()}
                        block
                        icon={<PlusOutlined />}
                      >
                        Add Option
                      </Button>
                    </Form.Item>
                  </>
                )}
              </Form.List>
            </StepContent>
          )}
          
          {currentStep === 3 && (
            <StepContent
              key="step-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Title level={5}>Review Quote</Title>
              <Paragraph>
                Please review the quote details before submission.
              </Paragraph>
              
              <Card size="small" title="Client Information" style={{ marginBottom: 16 }}>
                <p><strong>Name:</strong> {formData.clientName}</p>
                <p><strong>Email:</strong> {formData.email}</p>
                <p><strong>Phone:</strong> {formData.phone}</p>
              </Card>
              
              <Card size="small" title="Vehicle Details" style={{ marginBottom: 16 }}>
                <p><strong>Make:</strong> {formData.vehicleDetails?.make}</p>
                <p><strong>Model:</strong> {formData.vehicleDetails?.model}</p>
                <p><strong>Year:</strong> {formData.vehicleDetails?.year}</p>
                <p><strong>VIN:</strong> {formData.vehicleDetails?.vin}</p>
              </Card>
              
              <Card size="small" title="Coverage Details" style={{ marginBottom: 16 }}>
                <p><strong>Type:</strong> {formData.coverage?.type}</p>
                <p><strong>Duration:</strong> {formData.coverage?.duration} months</p>
                <p><strong>Start Date:</strong> {formData.coverage?.startDate?.toString()}</p>
                
                {formData.additionalOptions && formData.additionalOptions.length > 0 && (
                  <>
                    <Divider style={{ margin: '12px 0' }} />
                    <p><strong>Additional Options:</strong></p>
                    <ul>
                      {formData.additionalOptions.map((option, index) => (
                        <li key={index}>
                          {option.name}: ${option.cost}
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </Card>
              
              <Alert
                message="Ready to Submit"
                description="Please review all information for accuracy before submitting the quote."
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
            </StepContent>
          )}
        </AnimatePresence>
        
        <FormActions>
          {currentStep > 0 && (
            <Button 
              onClick={handlePrevious}
              icon={<LeftOutlined />}
              aria-label="Previous step"
            >
              Previous
            </Button>
          )}
          
          {currentStep < 3 ? (
            <Button 
              type="primary" 
              onClick={handleNext}
              style={{ marginLeft: 'auto' }}
              icon={<RightOutlined />}
              aria-label="Next step"
            >
              Next
            </Button>
          ) : (
            <Button 
              type="primary" 
              htmlType="submit"
              style={{ marginLeft: 'auto' }}
              loading={createQuoteMutation.isLoading}
              icon={<CheckCircleOutlined />}
              aria-label="Submit quote"
            >
              Submit Quote
            </Button>
          )}
        </FormActions>
      </StyledForm>
    </StyledCard>
  );
};
