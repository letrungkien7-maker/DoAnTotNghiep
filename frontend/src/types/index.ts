export interface DatabaseHealth {
  status: 'connected' | 'disconnected';
  dialect: string;
  latency_ms: number;
  error: string | null;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  app_name: string;
  environment: string;
  version: string;
  database: DatabaseHealth;
  timestamp: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}
