import { apiClient } from './apiClient';
import { InteractionType, DealStage } from './types';

// Types
export interface Interaction {
  id: number;
  customerId: number;
  type: InteractionType;
  description: string;
  agentId: number;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

export interface Deal {
  id: number;
  customerId: number;
  title: string;
  description?: string;
  stage: DealStage;
  value?: number;
  probability?: number;
  expectedCloseDate?: string;
  actualCloseDate?: string;
  createdBy: number;
  completedBy?: number;
  rejectedBy?: number;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

export interface PipelineStats {
  stages: Array<{
    stage: DealStage;
    count: number;
    value: number;
  }>;
  totalDeals: number;
  totalValue: number;
  winRate: number;
}

export interface CustomerCRMStats {
  totalInteractions: number;
  lastInteraction?: string;
  activeDeals: number;
  totalDealValue: number;
  activeDealValue: number;
  wonDealValue: number;
  successRate: number;
}

export interface CustomerWithCRMStats {
  id: number;
  name: string;
  company: string;
  email: string;
  phone: string;
  totalDealValue: number;
  wonDealValue: number;
  activeDeals: number;
  successRate: number;
  lastInteraction: string | null;
}

// API Functions
export const crmApi = {
  // Interactions
  createInteraction: async (customerId: number, data: {
    type: InteractionType;
    description: string;
    metadata?: Record<string, any>;
  }): Promise<Interaction> => {
    const response = await apiClient.post(`/customers/${customerId}/interactions`, data);
    return response.data;
  },

  getCustomerInteractions: async (
    customerId: number,
    params?: {
      days?: number;
      interactionType?: InteractionType;
    }
  ): Promise<Interaction[]> => {
    const response = await apiClient.get(`/customers/${customerId}/interactions`, { params });
    return response.data;
  },

  // Deals
  createDeal: async (customerId: number, data: {
    title: string;
    description?: string;
    value?: number;
    probability?: number;
    expectedCloseDate?: string;
    metadata?: Record<string, any>;
  }): Promise<Deal> => {
    const response = await apiClient.post(`/customers/${customerId}/deals`, data);
    return response.data;
  },

  getCustomerDeals: async (customerId: number): Promise<Deal[]> => {
    const response = await apiClient.get(`/customers/${customerId}/deals`);
    return response.data;
  },

  updateDeal: async (dealId: number, data: {
    title?: string;
    stage?: DealStage;
    metadata?: Record<string, any>;
  }): Promise<Deal> => {
    const response = await apiClient.patch(`/deals/${dealId}`, data);
    return response.data;
  },

  getDealsByStage: async (): Promise<Record<DealStage, Deal[]>> => {
    const response = await apiClient.get('/deals/by-stage');
    return response.data;
  },

  // Pipeline Stats
  getPipelineStats: async (): Promise<PipelineStats> => {
    const response = await apiClient.get('/pipeline/stats');
    return response.data;
  },

  // Customer CRM Stats
  getCustomerCRMStats: async (customerId: number): Promise<CustomerCRMStats> => {
    const response = await apiClient.get(`/customers/${customerId}/crm-stats`);
    return response.data;
  },

  // Customers
  getCustomersWithStats: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<CustomerWithCRMStats[]> => {
    const response = await apiClient.get('/crm/customers', { params });
    return response.data;
  }
};
