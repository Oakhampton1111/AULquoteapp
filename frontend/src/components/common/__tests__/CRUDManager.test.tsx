import React from 'react';
import { screen, fireEvent, waitFor, act } from '@testing-library/react';
import { CRUDManager } from '../CRUDManager';
import { renderWithProviders } from '../../../tests/utils/test-utils';

// Mock Ant Design components
jest.mock('antd', () => {
  // Mock message component
  const message = {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
    warning: jest.fn(),
    loading: jest.fn(),
  };

  // Create a simple mock for Modal
  const Modal = ({ title, open, onCancel, footer, children }: any) => {
    if (!open) return null;
    return (
      <div role="dialog" aria-modal="true" data-testid="modal">
        <div data-testid="modal-title">{title}</div>
        <div data-testid="modal-content">{children}</div>
        {footer}
        <button onClick={onCancel} data-testid="modal-close">Close Modal</button>
      </div>
    );
  };

  // Create a simple mock for Table
  const Table = ({ columns, dataSource, loading, rowKey }: any) => (
    <table data-testid="table">
      <thead>
        <tr>
          {columns.map((col: any, i: number) => (
            <th key={i}>{col.title}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {dataSource?.map((item: any, i: number) => (
          <tr key={i} data-testid={`row-${item[rowKey]}`}>
            {columns.map((col: any, j: number) => (
              <td key={j} data-testid={`cell-${col.dataIndex || 'action'}-${item[rowKey]}`}>
                {col.render ? col.render(null, item) : item[col.dataIndex]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );

  // Create a simple mock for Popconfirm
  const Popconfirm = ({ title, onConfirm, okText, cancelText, children }: any) => (
    <div data-testid="popconfirm">
      <div data-testid="popconfirm-trigger">{children}</div>
      <div data-testid="popconfirm-content">
        <div data-testid="popconfirm-title">{title}</div>
        <button onClick={onConfirm} data-testid="popconfirm-ok">{okText}</button>
        <button data-testid="popconfirm-cancel">{cancelText}</button>
      </div>
    </div>
  );

  return {
    message,
    Modal,
    Table,
    Popconfirm,
    Card: ({ title, children }: any) => (
      <div data-testid="card">
        <h2 data-testid="card-title">{title}</h2>
        <div data-testid="card-content">{children}</div>
      </div>
    ),
    Button: ({ type, icon, onClick, danger, children }: any) => (
      <button
        onClick={onClick}
        data-testid={`button-${children?.toString().toLowerCase().replace(/\s+/g, '-')}`}
        data-type={type}
        data-danger={danger ? 'true' : 'false'}
      >
        {icon}
        {children}
      </button>
    ),
    Space: ({ children }: any) => <div data-testid="space">{children}</div>,
    Form: {
      Item: ({ children }: any) => <div data-testid="form-item">{children}</div>,
    },
  };
});

// Mock components and data
interface TestItem {
  id: number;
  name: string;
}

const MockForm: React.FC<any> = ({ onSubmit, onCancel, initialValues }) => (
  <form onSubmit={(e) => { e.preventDefault(); onSubmit({ name: 'Test Item' }); }}>
    <input
      type="text"
      defaultValue={initialValues?.name || ''}
      data-testid="form-input"
    />
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

// Mock API functions
const mockCreateMutation = jest.fn().mockResolvedValue({ id: 3, name: 'Test Item' });
const mockUpdateMutation = jest.fn().mockResolvedValue({ id: 1, name: 'Updated Item' });
const mockDeleteMutation = jest.fn().mockResolvedValue(undefined);

describe('CRUDManager', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Mock useQuery hook for testing
  const mockUseQuery = () => ({
    data: mockData,
    isLoading: false,
  });

  const renderComponent = (props = {}) => {
    return renderWithProviders(
      <CRUDManager<TestItem>
        title="Test Items"
        useQuery={mockUseQuery}
        columns={mockColumns}
        createMutation={mockCreateMutation}
        updateMutation={mockUpdateMutation}
        deleteMutation={mockDeleteMutation}
        FormComponent={MockForm}
        queryKey={['test-items']}
        {...props}
      />
    );
  };

  it('renders the component with initial data', () => {
    renderComponent();

    // Check if the title is rendered
    expect(screen.getByTestId('card-title')).toHaveTextContent('Test Items');

    // Check if the table is rendered
    expect(screen.getByTestId('table')).toBeInTheDocument();

    // Check if the data is rendered in the table
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();

    // Check if action buttons are rendered
    expect(screen.getAllByText('Edit').length).toBe(2);
    expect(screen.getAllByText('Delete').length).toBe(2);
  });

  it('shows loading state when data is loading', () => {
    // Create a custom mock for loading state
    const loadingMockUseQuery = () => ({
      data: undefined,
      isLoading: true,
    });

    renderComponent({ useQuery: loadingMockUseQuery });

    // Title should still be visible
    expect(screen.getByTestId('card-title')).toHaveTextContent('Test Items');

    // Data should not be visible
    expect(screen.queryByText('Item 1')).not.toBeInTheDocument();
  });

  it('opens create form modal when add button is clicked', () => {
    renderComponent();

    // Find and click the Add New button
    const addButton = screen.getByTestId('button-add-new');
    fireEvent.click(addButton);

    // Check if the modal is displayed
    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByTestId('modal-title')).toHaveTextContent('Add Test Items');

    // Check if the form is displayed
    expect(screen.getByTestId('form-input')).toBeInTheDocument();
    expect(screen.getByText('Submit')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls create mutation when form is submitted', async () => {
    // Mock the createMutation function
    mockCreateMutation.mockImplementation((data) => {
      return Promise.resolve({ id: 3, ...data });
    });

    renderComponent();

    // Find and click the Add New button
    const addButton = screen.getByTestId('button-add-new');
    fireEvent.click(addButton);

    // Fill out the form
    const nameInput = screen.getByTestId('form-input');
    fireEvent.change(nameInput, { target: { value: 'Test Item' } });

    // Find and click the Submit button
    const submitButton = screen.getByText('Submit');
    await act(async () => {
      fireEvent.click(submitButton);
    });

    // Check if the create mutation was called with the correct data
    expect(mockCreateMutation).toHaveBeenCalledWith({ name: 'Test Item' });

    // Check if the modal is closed after submission
    await waitFor(() => {
      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });
  });

  it('opens edit form modal with correct data when edit button is clicked', () => {
    renderComponent();

    // Find and click the first Edit button
    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);

    // Check if the modal is displayed with the correct title
    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByTestId('modal-title')).toHaveTextContent('Edit Test Items');

    // Check if the form is displayed with the correct initial values
    const input = screen.getByTestId('form-input') as HTMLInputElement;
    expect(input.value).toBe('Item 1');
  });

  it('calls update mutation when edit form is submitted', async () => {
    // Mock the updateMutation function
    mockUpdateMutation.mockImplementation((data) => {
      return Promise.resolve(data);
    });

    renderComponent();

    // Find and click the first Edit button
    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);

    // Update the form input
    const nameInput = screen.getByTestId('form-input');
    fireEvent.change(nameInput, { target: { value: 'Test Item' } });

    // Find and click the Submit button
    const submitButton = screen.getByText('Submit');
    await act(async () => {
      fireEvent.click(submitButton);
    });

    // Check if the update mutation was called with the correct data
    expect(mockUpdateMutation).toHaveBeenCalledWith({ id: 1, name: 'Test Item' });

    // Check if the modal is closed after submission
    await waitFor(() => {
      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });
  });

  it('shows confirmation dialog when delete button is clicked', () => {
    renderComponent();

    // Find and click the first Delete button
    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    // Check if the confirmation dialog is displayed
    // Use getAllByTestId since there might be multiple popconfirm elements
    const popconfirmContents = screen.getAllByTestId('popconfirm-content');
    expect(popconfirmContents.length).toBeGreaterThan(0);

    const popconfirmTitles = screen.getAllByTestId('popconfirm-title');
    expect(popconfirmTitles[0]).toHaveTextContent('Are you sure you want to delete this item?');

    const okButtons = screen.getAllByTestId('popconfirm-ok');
    expect(okButtons[0]).toHaveTextContent('Yes');

    const cancelButtons = screen.getAllByTestId('popconfirm-cancel');
    expect(cancelButtons[0]).toHaveTextContent('No');
  });

  it('calls delete mutation when confirmation is confirmed', async () => {
    // Mock the deleteMutation function
    mockDeleteMutation.mockImplementation((id) => {
      return Promise.resolve({ id });
    });

    renderComponent();

    // Find and click the first Delete button
    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);

    // Find and click the Yes button (use getAllByTestId since there might be multiple)
    const yesButtons = screen.getAllByTestId('popconfirm-ok');
    await act(async () => {
      fireEvent.click(yesButtons[0]);
    });

    // Check if the delete mutation was called with the correct id
    expect(mockDeleteMutation).toHaveBeenCalledWith(1);
  });

  it('closes modal when cancel button is clicked', () => {
    renderComponent();

    // Find and click the Add New button
    const addButton = screen.getByTestId('button-add-new');
    fireEvent.click(addButton);

    // Check if the modal is displayed
    expect(screen.getByTestId('modal')).toBeInTheDocument();

    // Find and click the Cancel button
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    // Check if the modal is closed
    expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
  });
});
