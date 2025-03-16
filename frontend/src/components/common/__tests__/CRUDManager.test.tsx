import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CRUDManager } from '../CRUDManager';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock components and data
interface TestItem {
  id: number;
  name: string;
}

const MockForm: React.FC<any> = ({ onSubmit, onCancel, initialValues }) => (
  <form onSubmit={(e) => { e.preventDefault(); onSubmit({ name: 'Test Item' }); }}>
    <input type="text" defaultValue={initialValues?.name || ''} />
    <button type="submit">Submit</button>
    <button type="button" onClick={onCancel}>Cancel</button>
  </form>
);

const mockColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
  },
];

const mockData: TestItem[] = [
  { id: 1, name: 'Item 1' },
  { id: 2, name: 'Item 2' },
];

const mockUseQuery = () => ({
  data: mockData,
  isLoading: false,
});

const mockCreateMutation = jest.fn();
const mockUpdateMutation = jest.fn();
const mockDeleteMutation = jest.fn();

describe('CRUDManager', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    jest.clearAllMocks();
  });

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <CRUDManager<TestItem>
          title="Test Items"
          useQuery={mockUseQuery}
          columns={mockColumns}
          createMutation={mockCreateMutation}
          updateMutation={mockUpdateMutation}
          deleteMutation={mockDeleteMutation}
          FormComponent={MockForm}
          queryKey={['test-items']}
        />
      </QueryClientProvider>
    );
  };

  it('renders the component with initial data', () => {
    renderComponent();
    expect(screen.getByText('Test Items')).toBeInTheDocument();
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
  });

  it('opens create form modal when add button is clicked', () => {
    renderComponent();
    fireEvent.click(screen.getByText('Add New'));
    expect(screen.getByText('Add Test Items')).toBeInTheDocument();
  });

  it('calls create mutation when form is submitted', async () => {
    renderComponent();
    fireEvent.click(screen.getByText('Add New'));
    fireEvent.click(screen.getByText('Submit'));

    await waitFor(() => {
      expect(mockCreateMutation).toHaveBeenCalledWith({ name: 'Test Item' });
    });
  });

  it('calls update mutation when editing an item', async () => {
    renderComponent();
    fireEvent.click(screen.getAllByText('Edit')[0]);
    fireEvent.click(screen.getByText('Submit'));

    await waitFor(() => {
      expect(mockUpdateMutation).toHaveBeenCalledWith({ id: 1, name: 'Test Item' });
    });
  });

  it('calls delete mutation when deleting an item', async () => {
    renderComponent();
    fireEvent.click(screen.getAllByText('Delete')[0]);
    fireEvent.click(screen.getByText('Yes'));

    await waitFor(() => {
      expect(mockDeleteMutation).toHaveBeenCalledWith(1);
    });
  });

  it('closes modal when cancel is clicked', () => {
    renderComponent();
    fireEvent.click(screen.getByText('Add New'));
    fireEvent.click(screen.getByText('Cancel'));
    expect(screen.queryByText('Add Test Items')).not.toBeInTheDocument();
  });
});
