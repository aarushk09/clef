export interface User {
  id: string;
  email: string;
  name: string;
  credits: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiKey {
  id: string;
  userId: string;
  key: string;
  name: string;
  isActive: boolean;
  createdAt: Date;
  lastUsed?: Date;
  usageCount: number;
}

export interface ApiRequest {
  id: string;
  userId: string;
  apiKeyId: string;
  endpoint: string;
  method: string;
  requestBody?: any;
  responseBody?: any;
  statusCode: number;
  creditsUsed: number;
  timestamp: Date;
  processingTime: number;
}

export interface UsageStats {
  totalRequests: number;
  totalCreditsUsed: number;
  requestsToday: number;
  creditsUsedToday: number;
  averageResponseTime: number;
  successRate: number;
}

export interface VisionRequest {
  image?: string; // base64 encoded image (optional)
  prompt: string;
  maxTokens?: number;
  temperature?: number;
}

export interface VisionResponse {
  result: string;
  creditsUsed: number;
  processingTime: number;
}
