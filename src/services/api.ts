import axios from 'axios';
import type {
  TokenUsage,
  LatencyData,
  ErrorData,
  FeedbackItem,
  DashboardStats,
  SystemSettings,
  User,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------- Auth Service ----------
export const authService = {
  login: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    const res = await api.post('/auth/login', { email, password });
    const data = res.data as {
      access_token: string;
      token_type: string;
      user: { id: number; email: string; role: 'admin' | 'viewer'; created_at: string };
    };
    const user: User = {
      id: String(data.user.id),
      email: data.user.email,
      name: data.user.email.split('@')[0],
      role: data.user.role,
    };
    return { token: data.access_token, user };
  },
};

// ---------- Dashboard / Metrics ----------
export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await api.get('/metrics/summary');
    const d = res.data as {
      total_tokens: number;
      total_cost: number;
      average_latency: number;
      error_rate: number;
    };
    return {
      totalTokens: d.total_tokens,
      totalCost: d.total_cost,
      averageLatency: d.average_latency,
      errorRate: d.error_rate,
    };
  },

  getTokenUsage: async (): Promise<TokenUsage[]> => {
    const res = await api.get('/metrics/token-usage');
    const d = res.data as { data: { date: string; tokens: number; cost: number }[] };
    return d.data.map((p) => ({ date: p.date, tokens: p.tokens, cost: p.cost }));
  },

  getLatencyData: async (): Promise<LatencyData[]> => {
    const res = await api.get('/metrics/latency');
    const d = res.data as { data: { range: string; count: number }[] };
    return d.data.map((p) => ({ range: p.range, count: p.count }));
  },

  getErrorData: async (): Promise<ErrorData[]> => {
    const res = await api.get('/metrics/error-rate');
    const d = res.data as { data: { date: string; error_rate: number; total_requests: number }[] };
    return d.data.map((p) => ({ date: p.date, errorRate: p.error_rate, totalRequests: p.total_requests }));
  },
};

// ---------- Feedback ----------
export const feedbackService = {
  getFeedback: async (): Promise<FeedbackItem[]> => {
    const res = await api.get('/feedback');
    const items = res.data as Array<{
      id: number;
      llm_call_id: number;
      user_id: number;
      rating: number;
      comment: string | null;
      created_at: string;
    }>;
    // Map to UI type; prompt/response not in backend response, leave empty
    return items.map((f) => ({
      id: String(f.id),
      timestamp: f.created_at,
      user: `user-${f.user_id}`,
      model: 'LLM Model',
      rating: f.rating,
      comment: f.comment || '',
      prompt: '',
      response: '',
    }));
  },

  submitFeedback: async (feedback: { llm_call_id: number; rating: number; comment?: string }): Promise<void> => {
    await api.post('/feedback', feedback);
  },
};

// ---------- Settings (Admin) ----------
export const settingsService = {
  getSettings: async (): Promise<SystemSettings> => {
    const res = await api.get('/settings');
    const s = res.data as {
      id: number;
      claude_haiku_45_enabled: boolean;
      max_tokens_per_request: number;
      enable_caching: boolean;
      updated_at: string;
    };
    return {
      claudeHaiku45Enabled: s.claude_haiku_45_enabled,
      maxTokensPerRequest: s.max_tokens_per_request,
      enableCaching: s.enable_caching,
    };
  },

  updateSettings: async (settings: SystemSettings): Promise<void> => {
    const payload = {
      claude_haiku_45_enabled: settings.claudeHaiku45Enabled,
      max_tokens_per_request: settings.maxTokensPerRequest,
      enable_caching: settings.enableCaching,
    };
    await api.put('/settings', payload);
  },
};

export default api;
