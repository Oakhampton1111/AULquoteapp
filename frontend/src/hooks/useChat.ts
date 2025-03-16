import { useState, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Message } from '../types/chat';

interface ChatResponse {
  message: string;
  quote?: any;
  suggestions?: string[];
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Query for loading initial context
  const { data: initialContext } = useQuery(
    ['chatContext'],
    async () => {
      const response = await fetch('/api/v1/chat/context');
      if (!response.ok) throw new Error('Failed to load chat context');
      return response.json();
    },
    {
      onError: (err) => {
        console.error('Failed to load chat context:', err);
        setError('Failed to load chat context. Please try again.');
      }
    }
  );
  
  // Mutation for sending messages
  const sendMessageMutation = useMutation(
    async (content: string): Promise<ChatResponse> => {
      const response = await fetch('/api/v1/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          context: initialContext
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send message');
      }
      
      return response.json();
    },
    {
      onMutate: () => {
        setIsTyping(true);
        setError(null);
      },
      onError: (err) => {
        console.error('Failed to send message:', err);
        setError('Failed to send message. Please try again.');
        setIsTyping(false);
      },
      onSettled: () => {
        setIsTyping(false);
      }
    }
  );
  
  const sendMessage = useCallback(
    async (content: string) => {
      // Add user message immediately
      const userMessage: Message = {
        role: 'user',
        content,
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, userMessage]);
      
      try {
        const response = await sendMessageMutation.mutateAsync(content);
        
        // Add assistant message with any quote data
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.message,
          timestamp: new Date(),
          quote: response.quote
        };
        setMessages((prev) => [...prev, assistantMessage]);
        
        return response;
      } catch (err) {
        // Error is handled by mutation callbacks
        return null;
      }
    },
    [sendMessageMutation]
  );
  
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);
  
  return {
    messages,
    isLoading: sendMessageMutation.isLoading,
    isTyping,
    error,
    sendMessage,
    clearMessages
  };
};
