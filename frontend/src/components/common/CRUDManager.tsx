import React, { useState } from 'react';
import {
  Card,
  Form,
  Button,
  Space,
  Table,
  Modal,
  message,
  Popconfirm,
} from 'antd';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useMutation, useQueryClient, UseQueryResult } from '@tanstack/react-query';

interface CRUDManagerProps<T> {
  title: string;
  useQuery: () => UseQueryResult<T[], unknown>;
  columns: any[];
  createMutation: (data: any) => Promise<T>;
  updateMutation: (data: { id: number } & any) => Promise<T>;
  deleteMutation: (id: number) => Promise<void>;
  FormComponent: React.ComponentType<{
    initialValues?: T;
    onSubmit: (values: any) => void;
    onCancel: () => void;
  }>;
  queryKey: string[];
  addButtonText?: string;
  deleteConfirmText?: string;
}

export function CRUDManager<T extends { id: number }>({
  title,
  useQuery,
  columns,
  createMutation,
  updateMutation,
  deleteMutation,
  FormComponent,
  queryKey,
  addButtonText = 'Add New',
  deleteConfirmText = 'Are you sure you want to delete this item?'
}: CRUDManagerProps<T>) {
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<T | null>(null);
  const queryClient = useQueryClient();
  const { data: items, isLoading } = useQuery();

  const createMutate = useMutation(createMutation, {
    onSuccess: () => {
      message.success('Item created successfully');
      queryClient.invalidateQueries(queryKey);
      handleModalClose();
    },
    onError: (error: any) => {
      message.error(error.message || 'Failed to create item');
    },
  });

  const updateMutate = useMutation(updateMutation, {
    onSuccess: () => {
      message.success('Item updated successfully');
      queryClient.invalidateQueries(queryKey);
      handleModalClose();
    },
    onError: (error: any) => {
      message.error(error.message || 'Failed to update item');
    },
  });

  const deleteMutate = useMutation(deleteMutation, {
    onSuccess: () => {
      message.success('Item deleted successfully');
      queryClient.invalidateQueries(queryKey);
    },
    onError: (error: any) => {
      message.error(error.message || 'Failed to delete item');
    },
  });

  const handleModalClose = () => {
    setModalVisible(false);
    setEditingItem(null);
  };

  const handleEdit = (item: T) => {
    setEditingItem(item);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    deleteMutate.mutate(id);
  };

  const handleSubmit = async (values: any) => {
    if (editingItem) {
      updateMutate.mutate({ id: editingItem.id, ...values });
    } else {
      createMutate.mutate(values);
    }
  };

  const actionColumn = {
    title: 'Actions',
    key: 'actions',
    render: (_: any, record: T) => (
      <Space>
        <Button
          type="text"
          icon={<EditOutlined />}
          onClick={() => handleEdit(record)}
        >
          Edit
        </Button>
        <Popconfirm
          title={deleteConfirmText}
          onConfirm={() => handleDelete(record.id)}
          okText="Yes"
          cancelText="No"
        >
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
          >
            Delete
          </Button>
        </Popconfirm>
      </Space>
    ),
  };

  return (
    <Card title={title}>
      <div className="mb-4">
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          {addButtonText}
        </Button>
      </div>

      <Table
        columns={[...columns, actionColumn]}
        dataSource={items}
        loading={isLoading}
        rowKey="id"
      />

      <Modal
        title={editingItem ? `Edit ${title}` : `Add ${title}`}
        open={modalVisible}
        onCancel={handleModalClose}
        footer={null}
      >
        <FormComponent
          initialValues={editingItem || undefined}
          onSubmit={handleSubmit}
          onCancel={handleModalClose}
        />
      </Modal>
    </Card>
  );
}
