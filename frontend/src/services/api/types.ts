// Common API types

export enum InteractionType {
  CALL = 'CALL',
  EMAIL = 'EMAIL',
  MEETING = 'MEETING',
  NOTE = 'NOTE'
}

export enum DealStage {
  LEAD = 'LEAD',
  CONTACT = 'CONTACT',
  QUOTE_REQUESTED = 'QUOTE_REQUESTED',
  QUOTE_SENT = 'QUOTE_SENT',
  NEGOTIATION = 'NEGOTIATION',
  CLOSED_WON = 'CLOSED_WON',
  CLOSED_LOST = 'CLOSED_LOST'
}

export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, any>;
}
