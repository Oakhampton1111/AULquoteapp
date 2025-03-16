export type MessageType = 'customer' | 'admin' | 'system' | 'note';

export interface ConversationCreate {
  quote_id: number;
  user_id: number;
  message: string;
  message_type: MessageType;
  metadata?: Record<string, any>;
}

export interface Conversation extends ConversationCreate {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationFilter {
  quote_id?: number;
  user_id?: number;
  message_type?: MessageType;
  created_after?: string;
  created_before?: string;
}
