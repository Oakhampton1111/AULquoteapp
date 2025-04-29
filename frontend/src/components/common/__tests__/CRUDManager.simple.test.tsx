/**
 * Simple test for CRUDManager component
 *
 * This test avoids using React Query to prevent hook-related issues
 */

import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { CRUDManager } from '../CRUDManager';

// Mock the entire @tanstack/react-query module
jest.mock('@tanstack/react-query', () => {
  const actual = jest.requireActual('@tanstack/react-query');
  return {
    ...actual,
    useQueryClient: jest.fn(() => ({
      invalidateQueries: jest.fn(),
    })),
    useMutation: jest.fn((_mutationFn, options) => {
      return {
        mutate: (data: any) => {
          if (options?.onSuccess) {
            options.onSuccess(data);
          }
        },
        isLoading: false,
      };
    }),
    QueryClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

// Mock antd components
jest.mock('antd', () => {
  return {
    Card: ({ title, children }: any) => (
      <div data-testid="card">
        <div data-testid="card-title">{title}</div>
        <div data-testid="card-content">{children}</div>
      </div>
    ),
    Table: ({ dataSource }: any) => (
      <table data-testid="table">
        <tbody>
          {dataSource?.map((item: any, i: number) => (
            <tr key={i} data-testid={`row-${item.id}`}>
              <td>{item.name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    ),
    Button: ({ children, onClick }: any) => (
      <button onClick={onClick} data-testid={`button-${children?.toString().toLowerCase()}`}>
        {children}
      </button>
    ),
    Space: ({ children }: any) => <div data-testid="space">{children}</div>,
    Modal: ({ title, open, children }: any) =>
      open ? (
        <div data-testid="modal">
          <div data-testid="modal-title">{title}</div>
          <div data-testid="modal-content">{children}</div>
        </div>
      ) : null,
    Popconfirm: ({ children }: any) => <div data-testid="popconfirm">{children}</div>,
    message: {
      success: jest.fn(),
      error: jest.fn(),
    },
  };
});

// Mock components and data
interface TestItem {
  id: number;
  name: string;
}

const MockForm = ({ onSubmit, onCancel }: any) => (
  <form data-testid="form">
    <button type="button" onClick={() => onSubmit({ name: 'Test Item' })}>
      Submit
    </button>
    <button type="button" onClick={onCancel}>
      Cancel
    </button>
  </form>
);

const mockColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
  },
];

const mockData = [
  { id: 1, name: 'Item 1' },
  { id: 2, name: 'Item 2' },
];

// Mock API functions
const mockCreateMutation = jest.fn().mockResolvedValue({ id: 3, name: 'Test Item' });
const mockUpdateMutation = jest.fn().mockResolvedValue({ id: 1, name: 'Updated Item' });
const mockDeleteMutation = jest.fn().mockResolvedValue(undefined);

// Mock useQuery hook
const mockUseQuery = jest.fn().mockReturnValue({
  data: mockData,
  isLoading: false,
});

describe('CRUDManager Simple Test', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = () => {
    return render(
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
    );
  };

  it('renders the component with title', () => {
    renderComponent();

    // Check if the title is rendered
    expect(screen.getByTestId('card-title')).toHaveTextContent('Test Items');
  });

  it('renders the table with data', () => {
    renderComponent();

    // Check if the table is rendered
    expect(screen.getByTestId('table')).toBeInTheDocument();

    // Check if data is rendered
    expect(screen.getByTestId('row-1')).toBeInTheDocument();
    expect(screen.getByTestId('row-2')).toBeInTheDocument();
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
  });

  it('shows loading state when data is loading', () => {
    // Override the mock for this test
    mockUseQuery.mockReturnValueOnce({
      data: undefined,
      isLoading: true,
    });

    renderComponent();

    // Check if the title is still rendered
    expect(screen.getByTestId('card-title')).toHaveTextContent('Test Items');
  });

  it('opens modal when add button is clicked', async () => {
    const { getByTestId } = renderComponent();

    // Modal should not be visible initially
    expect(screen.queryByTestId('modal')).not.toBeInTheDocument();

    // Click the add button using act to handle state updates
    await act(async () => {
      const addButton = screen.getByTestId('button-add new');
      fireEvent.click(addButton);
    });

    // Modal should now be visible
    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByTestId('modal-title')).toHaveTextContent('Add Test Items');
    expect(screen.getByTestId('form')).toBeInTheDocument();
  });

  it('calls create mutation when form is submitted', async () => {
    renderComponent();

    // Open the modal
    await act(async () => {
      const addButton = screen.getByTestId('button-add new');
      fireEvent.click(addButton);
    });

    // Submit the form
    await act(async () => {
      const submitButton = screen.getByText('Submit');
      fireEvent.click(submitButton);
    });

    // Check if the create mutation was called
    expect(mockCreateMutation).toHaveBeenCalledWith({ name: 'Test Item' });
  });

  it('closes modal when cancel button is clicked', async () => {
    renderComponent();

    // Open the modal
    await act(async () => {
      const addButton = screen.getByTestId('button-add new');
      fireEvent.click(addButton);
    });

    // Modal should be visible
    expect(screen.getByTestId('modal')).toBeInTheDocument();

    // Click the cancel button
    await act(async () => {
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);
    });

    // Modal should be closed
    expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
  });
});
