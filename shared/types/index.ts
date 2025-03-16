// Common TypeScript interfaces shared between frontend and backend

export interface User {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    role: UserRole;
    createdAt: string;
    updatedAt: string;
}

export enum UserRole {
    ADMIN = 'admin',
    CUSTOMER = 'customer'
}

export interface Quote {
    id: string;
    customerId: string;
    status: QuoteStatus;
    items: QuoteItem[];
    totalAmount: number;
    createdAt: string;
    updatedAt: string;
    validUntil: string;
}

export enum QuoteStatus {
    DRAFT = 'draft',
    PENDING = 'pending',
    APPROVED = 'approved',
    REJECTED = 'rejected',
    EXPIRED = 'expired'
}

export interface QuoteItem {
    id: string;
    description: string;
    quantity: number;
    unitPrice: number;
    totalPrice: number;
}

export interface RateCard {
    id: string;
    name: string;
    description: string;
    validFrom: string;
    validUntil: string;
    rates: Rate[];
    status: RateCardStatus;
    createdAt: string;
    updatedAt: string;
}

export enum RateCardStatus {
    ACTIVE = 'active',
    INACTIVE = 'inactive',
    DRAFT = 'draft'
}

export interface Rate {
    id: string;
    service: string;
    baseRate: number;
    minimumCharge: number;
    conditions?: string[];
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: {
        code: string;
        message: string;
    };
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
}

export interface CustomerProfile {
    id: string;
    userId: string;
    company: string;
    industry: string;
    preferredServices: string[];
    specialRates: boolean;
    notes?: string;
    createdAt: string;
    updatedAt: string;
}

export interface AiQuoteRequest {
    requirements: string;
    context?: {
        customerProfile?: CustomerProfile;
        previousQuotes?: Quote[];
        specialInstructions?: string;
    };
}

export interface AiQuoteResponse {
    suggestedQuote: Quote;
    confidence: number;
    reasoning: string;
    alternatives?: Quote[];
}
