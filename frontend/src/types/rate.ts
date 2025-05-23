export interface Rate {
  id: number;
  name: string;
  description?: string;
  category: string;
  rate: number;
  unit: string;
  is_active: boolean;
}

export interface RateInput {
  name: string;
  description?: string;
  category: string;
  rate: number;
  unit: string;
  is_active?: boolean;
}
