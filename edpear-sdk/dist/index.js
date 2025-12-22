"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.EdPearClient = void 0;
exports.createEdPearClient = createEdPearClient;
const axios_1 = __importDefault(require("axios"));
class EdPearClient {
    constructor(config) {
        this.apiKey = config.apiKey;
        this.baseURL = config.baseURL || 'https://api.edpear.com';
    }
    /**
     * Analyze an image or process text using EdPear's AI
     * @param request - The request containing prompt and optional image
     * @returns Promise<VisionResponse>
     */
    async analyzeImage(request) {
        return this.processRequest(request);
    }
    /**
     * Send a chat/text request to EdPear's AI
     * @param prompt - The text prompt
     * @param options - Optional parameters like maxTokens and temperature
     * @returns Promise<VisionResponse>
     */
    async chat(prompt, options) {
        return this.processRequest({
            prompt,
            ...options
        });
    }
    async processRequest(request) {
        try {
            const response = await axios_1.default.post(`${this.baseURL}/api/vision`, request, {
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.apiKey,
                },
            });
            return response.data;
        }
        catch (error) {
            if (error.response?.status === 401) {
                throw new Error('Invalid API key. Please check your EdPear API key.');
            }
            else if (error.response?.status === 402) {
                throw new Error('Insufficient credits. Please add more credits to your account.');
            }
            else if (error.response?.status === 400) {
                throw new Error(`Bad request: ${error.response.data.error}`);
            }
            else {
                throw new Error(`API request failed: ${error.message}`);
            }
        }
    }
    /**
     * Get account status and remaining credits
     * @returns Promise<{credits: number, user: any}>
     */
    async getStatus() {
        try {
            const response = await axios_1.default.get(`${this.baseURL}/api/user/status`, {
                headers: {
                    'x-api-key': this.apiKey,
                },
            });
            return response.data;
        }
        catch (error) {
            throw new Error(`Failed to get account status: ${error.message}`);
        }
    }
}
exports.EdPearClient = EdPearClient;
// Convenience function for quick setup
function createEdPearClient(apiKey, baseURL) {
    return new EdPearClient({ apiKey, baseURL });
}
// Default export
exports.default = EdPearClient;
//# sourceMappingURL=index.js.map