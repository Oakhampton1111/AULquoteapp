export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  quote?: Record<string, any>; // Or a more specific type if the structure of a quote is known
}
