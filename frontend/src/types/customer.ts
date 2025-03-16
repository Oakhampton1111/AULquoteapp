export interface CustomerCreate {
  user_id: number;
  company_name?: string;
  contact_name: string;
  email: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  preferences?: Record<string, any>;
}

export interface Customer extends CustomerCreate {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface CustomerFilter {
  company_name?: string;
  email?: string;
  created_after?: string;
  created_before?: string;
}
