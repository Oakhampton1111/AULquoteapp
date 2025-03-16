/**
 * WebSocket client for real-time communication.
 */

export interface WebSocketMessage {
  type: string;
  payload: any;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000; // Start with 1 second
  private messageHandlers: Map<string, (payload: any) => void> = new Map();

  constructor(private token: string) {}

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws?token=${this.token}`;
    
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
  }

  private handleOpen() {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    this.reconnectTimeout = 1000;
  }

  private handleClose() {
    console.log('WebSocket closed');
    this.attemptReconnect();
  }

  private handleError(error: Event) {
    console.error('WebSocket error:', error);
    this.attemptReconnect();
  }

  private handleMessage(event: MessageEvent) {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(message.payload);
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
        this.connect();
        this.reconnectAttempts++;
        this.reconnectTimeout *= 2; // Exponential backoff
      }, this.reconnectTimeout);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  send(type: string, payload: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    }
  }

  onMessage(type: string, handler: (payload: any) => void) {
    this.messageHandlers.set(type, handler);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Create and export WebSocket instance
let wsClient: WebSocketClient | null = null;

export const getWebSocketClient = (token: string): WebSocketClient => {
  if (!wsClient) {
    wsClient = new WebSocketClient(token);
    wsClient.connect();
  }
  return wsClient;
};
