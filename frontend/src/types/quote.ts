import { RateCard } from './rateCard';

export type QuoteStatus = 'pending' | 'accepted' | 'rejected' | 'expired';
export type ServiceType = 'storage' | 'packing' | 'shipping' | 'combined';

interface StorageDetails {
  storage_type: 'climate_controlled' | 'standard' | 'specialized';
  duration_months: number;
  square_feet: number;
  special_requirements?: string;
}

interface PackingDetails {
  item_count: number;
  requires_special_handling: boolean;
  packing_materials: string[];
  special_instructions?: string;
}

interface ShippingDetails {
  origin_address: string;
  destination_address: string;
  weight_lbs: number;
  dimensions: {
    width: number;
    height: number;
    length: number;
  };
  shipping_method: string;
  special_handling?: string;
}

interface CombinedServiceDetails {
  services: Array<{
    type: ServiceType;
    details: StorageDetails | PackingDetails | ShippingDetails;
  }>;
}

export type ServiceDetails = 
  | StorageDetails 
  | PackingDetails 
  | ShippingDetails 
  | CombinedServiceDetails;

export interface QuoteCreate {
  customer_id: number;
  customer_email: string;
  customer_name: string;
  service_type: ServiceType;
  service_details: ServiceDetails;
  base_price: number;
  handling_fees?: number;
  tax_rate?: number;
  discount?: number;
  notes?: string;
}

export interface Quote extends QuoteCreate {
  id: number;
  quote_number: string;
  status: QuoteStatus;
  created_by_id: number;
  valid_until: string;
  accepted_at?: string;
  rejected_at?: string;
  created_at: string;
  updated_at: string;
  rate_cards: RateCard[];
  total_amount: number;
}

export interface QuoteFilter {
  status?: QuoteStatus;
  start_date?: string;
  end_date?: string;
}

export interface QuoteStatusUpdate {
  status: QuoteStatus;
  reason?: string;
}
