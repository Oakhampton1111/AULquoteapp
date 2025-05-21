export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string; // Or Date, ensure consistency with useChat.ts if possible
  // If useChat.ts uses Date, this should be Date. For now, only removing id.
  quote?: any; // Adding quote property from useChat.ts's Message type
}
