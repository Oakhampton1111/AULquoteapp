/**
 * Mock implementations for Ant Design components
 */
import React from 'react';

// Mock Table component
export const Table = ({ dataSource, columns, rowKey }: any) => (
  <div className="ant-table">
    <table>
      <thead>
        <tr>
          {columns.map((column: any) => (
            <th key={column.key}>{column.title}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {dataSource?.map((item: any) => (
          <tr key={rowKey ? item[rowKey] : item.id}>
            {columns.map((column: any) => (
              <td key={column.key}>
                {column.render ? column.render(item[column.dataIndex], item) : item[column.dataIndex]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// Mock Modal component
export const Modal = ({ 
  title, 
  visible, 
  onOk, 
  onCancel, 
  children 
}: any) => {
  if (!visible) return null;
  
  return (
    <div className="ant-modal">
      <div className="ant-modal-content">
        <div className="ant-modal-header">
          <div className="ant-modal-title">{title}</div>
        </div>
        <div className="ant-modal-body">{children}</div>
        <div className="ant-modal-footer">
          <button onClick={onCancel}>Cancel</button>
          <button onClick={onOk}>OK</button>
        </div>
      </div>
    </div>
  );
};

// Mock Button component
export const Button = ({ 
  type, 
  onClick, 
  children, 
  ...props 
}: any) => (
  <button 
    className={`ant-btn ant-btn-${type || 'default'}`} 
    onClick={onClick}
    {...props}
  >
    {children}
  </button>
);

// Mock Space component
export const Space = ({ children }: any) => (
  <div className="ant-space">{children}</div>
);

// Mock Spin component
export const Spin = ({ spinning, children }: any) => (
  <div className="ant-spin">
    {spinning && <div className="ant-spin-dot" />}
    {children}
  </div>
);

// Mock Alert component
export const Alert = ({ message, description, type }: any) => (
  <div className={`ant-alert ant-alert-${type}`}>
    <div className="ant-alert-message">{message}</div>
    <div className="ant-alert-description">{description}</div>
  </div>
);

// Mock message API
export const message = {
  success: jest.fn(),
  error: jest.fn(),
  info: jest.fn(),
  warning: jest.fn(),
  loading: jest.fn(),
};

// Mock Modal.confirm API
Modal.confirm = jest.fn(({ onOk, onCancel }) => {
  // Simulate clicking "Yes" immediately for testing
  if (onOk) onOk();
  return { destroy: jest.fn() };
});

// Export all components
export default {
  Table,
  Modal,
  Button,
  Space,
  Spin,
  Alert,
  message,
};
