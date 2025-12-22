import axios, { AxiosResponse } from 'axios';

export interface VisionRequest {
  image?: string; // base64 encoded image (optional)
  prompt: string;
  maxTokens?: number;
  temperature?: number;
}

export interface VisionResponse {
  success: boolean;
  result: string;
  creditsUsed: number;
  remainingCredits: number;
  processingTime: number;
}

export interface EdPearConfig {
  apiKey: string;
  baseURL?: string;
}

export class EdPearClient {
  private apiKey: string;
  private baseURL: string;

  constructor(config: EdPearConfig) {
    this.apiKey = config.apiKey;
    this.baseURL = config.baseURL || 'https://api.edpear.com';
  }

  /**
   * Analyze an image or process text using EdPear's AI
   * @param request - The request containing prompt and optional image
   * @returns Promise<VisionResponse>
   */
  async analyzeImage(request: VisionRequest): Promise<VisionResponse> {
    return this.processRequest(request);
  }

  /**
   * Send a chat/text request to EdPear's AI
   * @param prompt - The text prompt
   * @param options - Optional parameters like maxTokens and temperature
   * @returns Promise<VisionResponse>
   */
  async chat(prompt: string, options?: { maxTokens?: number; temperature?: number }): Promise<VisionResponse> {
    return this.processRequest({
      prompt,
      ...options
    });
  }

  private async processRequest(request: VisionRequest): Promise<VisionResponse> {
    try {
      const response: AxiosResponse<VisionResponse> = await axios.post(
        `${this.baseURL}/api/vision`,
        request,
        {
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': this.apiKey,
          },
        }
      );

      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Invalid API key. Please check your EdPear API key.');
      } else if (error.response?.status === 402) {
        throw new Error('Insufficient credits. Please add more credits to your account.');
      } else if (error.response?.status === 400) {
        throw new Error(`Bad request: ${error.response.data.error}`);
      } else {
        throw new Error(`API request failed: ${error.message}`);
      }
    }
  }

  /**
   * Get account status and remaining credits
   * @returns Promise<{credits: number, user: any}>
   */
  async getStatus(): Promise<{ credits: number; user: any }> {
    try {
      const response = await axios.get(`${this.baseURL}/api/user/status`, {
        headers: {
          'x-api-key': this.apiKey,
        },
      });

      return response.data;
    } catch (error: any) {
      throw new Error(`Failed to get account status: ${error.message}`);
    }
  }
}

// Convenience function for quick setup
export function createEdPearClient(apiKey: string, baseURL?: string): EdPearClient {
  return new EdPearClient({ apiKey, baseURL });
}

// Default export
export default EdPearClient;
