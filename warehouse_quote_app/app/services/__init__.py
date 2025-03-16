"""
Services package initialization.

This package provides various services for the application:
1. Business Logic
   - Quote generation and management
   - Rate card management
2. Communication
   - Email service
   - Realtime WebSocket service
3. LLM Integration
   - Chat service
   - RAG implementation
   - Rate optimization
4. Metrics and Monitoring
   - System metrics collection
   - Health monitoring
5. Conversation Handling
   - Conversation state management
"""

from .base import BaseService
from .business import QuoteService, RateService
from .communication import EmailService, RealtimeService
from .llm import ChatService, RateOptimizer
from .metrics import MetricsService
from .conversation import ConversationState, ConversationContext, ConversationResponse

__all__ = [
    'BaseService',
    'QuoteService',
    'RateService',
    'EmailService',
    'RealtimeService',
    'ChatService',
    'RateOptimizer',
    'MetricsService',
    'ConversationState',
    'ConversationContext',
    'ConversationResponse'
]
