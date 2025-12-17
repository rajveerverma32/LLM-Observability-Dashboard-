export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'viewer';
}

export interface TokenUsage {
  date: string;
  tokens: number;
  cost: number;
}

export interface LatencyData {
  range: string;
  count: number;
}

export interface ErrorData {
  date: string;
  errorRate: number;
  totalRequests: number;
}

export interface FeedbackItem {
  id: string;
  timestamp: string;
  user: string;
  model: string;
  rating: number;
  comment: string;
  prompt: string;
  response: string;
}

export interface DashboardStats {
  totalTokens: number;
  totalCost: number;
  averageLatency: number;
  errorRate: number;
}

export interface SystemSettings {
  claudeHaiku45Enabled: boolean;
  maxTokensPerRequest: number;
  enableCaching: boolean;
}
