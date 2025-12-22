export interface VisionRequest {
    image?: string;
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
export declare class EdPearClient {
    private apiKey;
    private baseURL;
    constructor(config: EdPearConfig);
    /**
     * Analyze an image or process text using EdPear's AI
     * @param request - The request containing prompt and optional image
     * @returns Promise<VisionResponse>
     */
    analyzeImage(request: VisionRequest): Promise<VisionResponse>;
    /**
     * Send a chat/text request to EdPear's AI
     * @param prompt - The text prompt
     * @param options - Optional parameters like maxTokens and temperature
     * @returns Promise<VisionResponse>
     */
    chat(prompt: string, options?: {
        maxTokens?: number;
        temperature?: number;
    }): Promise<VisionResponse>;
    private processRequest;
    /**
     * Get account status and remaining credits
     * @returns Promise<{credits: number, user: any}>
     */
    getStatus(): Promise<{
        credits: number;
        user: any;
    }>;
}
export declare function createEdPearClient(apiKey: string, baseURL?: string): EdPearClient;
export default EdPearClient;
//# sourceMappingURL=index.d.ts.map