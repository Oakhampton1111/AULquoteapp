import { Rule } from 'antd/es/form';
import { validators } from '@shared/utils';

export const validationRules = {
  required: (message: string): Rule => ({
    required: true,
    message,
  }),

  email: (): Rule => ({
    validator: async (_, value) => {
      if (!value || validators.isValidEmail(value)) {
        return Promise.resolve();
      }
      return Promise.reject(new Error('Please enter a valid email address'));
    },
  }),

  password: (): Rule => ({
    validator: async (_, value) => {
      if (!value || validators.isStrongPassword(value)) {
        return Promise.resolve();
      }
      return Promise.reject(new Error('Password must be at least 8 characters and include uppercase, lowercase, number, and special character'));
    },
  }),

  phone: (): Rule => ({
    validator: async (_, value) => {
      if (!value || validators.isValidPhone(value)) {
        return Promise.resolve();
      }
      return Promise.reject(new Error('Please enter a valid phone number'));
    },
  }),

  vin: (): Rule => ({
    validator: async (_, value) => {
      if (!value || validators.isValidVIN(value)) {
        return Promise.resolve();
      }
      return Promise.reject(new Error('Please enter a valid 17-character VIN'));
    },
  }),

  year: (): Rule => ({
    validator: async (_, value) => {
      if (!value || validators.isValidYear(Number(value))) {
        return Promise.resolve();
      }
      return Promise.reject(new Error('Please enter a valid year between 1900 and current year + 1'));
    },
  }),

  currency: (): Rule => ({
    validator: async (_, value) => {
      if (!value || validators.isValidCurrency(Number(value))) {
        return Promise.resolve();
      }
      return Promise.reject(new Error('Please enter a valid currency amount'));
    },
  }),

  name: (): Rule => ({
    type: 'string',
    min: 2,
    message: 'Name must be at least 2 characters',
  }),
};
