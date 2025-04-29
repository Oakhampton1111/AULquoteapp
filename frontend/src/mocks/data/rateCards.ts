import { RateCard } from '../../types/rateCard';

export const mockRateCards: RateCard[] = [
  {
    id: 'rate-1',
    name: 'Standard Storage',
    description: 'Basic coverage for stored vehicles',
    baseCost: 100,
    coverageDetails: [
      { type: 'Damage', description: 'Coverage for damage while in storage', included: true },
      { type: 'Theft', description: 'Coverage for theft while in storage', included: true }
    ],
    durationOptions: [
      { months: 12, multiplier: 1.0 },
      { months: 24, multiplier: 1.8 },
      { months: 36, multiplier: 2.5 }
    ],
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-01T00:00:00Z',
    isActive: true
  },
  {
    id: 'rate-2',
    name: 'Premium Storage',
    description: 'Enhanced coverage for stored vehicles',
    baseCost: 200,
    coverageDetails: [
      { type: 'Damage', description: 'Coverage for damage while in storage', included: true },
      { type: 'Theft', description: 'Coverage for theft while in storage', included: true },
      { type: 'Natural Disasters', description: 'Coverage for natural disasters', included: true }
    ],
    durationOptions: [
      { months: 12, multiplier: 1.0 },
      { months: 24, multiplier: 1.8 },
      { months: 36, multiplier: 2.5 }
    ],
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-01T00:00:00Z',
    isActive: true
  },
  {
    id: 'rate-3',
    name: 'Basic Transport',
    description: 'Basic coverage for vehicle transport',
    baseCost: 150,
    coverageDetails: [
      { type: 'Damage', description: 'Coverage for damage during transport', included: true },
      { type: 'Theft', description: 'Coverage for theft during transport', included: true }
    ],
    durationOptions: [
      { months: 12, multiplier: 1.0 },
      { months: 24, multiplier: 1.8 },
      { months: 36, multiplier: 2.5 }
    ],
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-01T00:00:00Z',
    isActive: true
  }
];
