import { Quote } from '../../types/quote';

export const mockQuotes: Quote[] = [
  {
    id: 'quote-1',
    clientInfo: {
      name: 'John Doe',
      email: 'john.doe@example.com',
      phone: '555-123-4567',
    },
    vehicleDetails: {
      make: 'Toyota',
      model: 'Camry',
      year: 2022,
      vin: '1HGCM82633A123456',
    },
    coverage: {
      type: 'rate-1',
      startDate: '2023-01-01T00:00:00Z',
      durationMonths: 12,
    },
    additionalOptions: [
      {
        name: 'Roadside Assistance',
        cost: 50,
      },
    ],
    totalCost: 150,
    status: 'active',
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-01T00:00:00Z',
  },
  {
    id: 'quote-2',
    clientInfo: {
      name: 'Jane Smith',
      email: 'jane.smith@example.com',
      phone: '555-987-6543',
    },
    vehicleDetails: {
      make: 'Honda',
      model: 'Accord',
      year: 2021,
      vin: '5J8TB4H36LL000000',
    },
    coverage: {
      type: 'rate-2',
      startDate: '2023-02-01T00:00:00Z',
      durationMonths: 24,
    },
    additionalOptions: [
      {
        name: 'Extended Warranty',
        cost: 100,
      },
      {
        name: 'Rental Car Coverage',
        cost: 75,
      },
    ],
    totalCost: 375,
    status: 'pending',
    createdAt: '2023-02-01T00:00:00Z',
    updatedAt: '2023-02-01T00:00:00Z',
  },
];
