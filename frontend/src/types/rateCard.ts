export interface RateCard {
  id: string;
  name: string;
  description: string;
  baseCost: number;
  coverageDetails: {
    type: string;
    description: string;
    included: boolean;
  }[];
  durationOptions: {
    months: number;
    multiplier: number;
  }[];
  restrictions?: {
    maxAge?: number;
    maxMileage?: number;
    vehicleTypes?: string[];
  };
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}
