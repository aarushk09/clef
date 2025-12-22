# EdPear SDK

JavaScript/TypeScript SDK for EdPear - AI-powered educational components.

## Installation

```bash
npm install @edpear/sdk
```

## Quick Start

```javascript
const { EdPearClient } = require('@edpear/sdk');

const client = new EdPearClient({
  apiKey: process.env.EDPEAR_API_KEY
});

// Analyze an image
const result = await client.analyzeImage({
  image: base64Image,
  prompt: "Analyze this textbook page and explain the main concepts"
});

console.log(result.result);
```

## API Reference

### EdPearClient

#### Constructor

```javascript
const client = new EdPearClient({
  apiKey: string,        // Required: Your EdPear API key
  baseURL?: string       // Optional: API base URL (default: https://api.edpear.com)
});
```

#### Methods

##### analyzeImage(request)

Analyze an image using EdPear's Vision AI.

**Parameters:**
- `request.image` (string): Base64 encoded image
- `request.prompt` (string): Analysis prompt
- `request.maxTokens` (number, optional): Maximum tokens in response (default: 1000)
- `request.temperature` (number, optional): Response creativity (0-1, default: 0.7)

**Returns:** Promise<VisionResponse>

**Example:**
```javascript
const result = await client.analyzeImage({
  image: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...',
  prompt: 'Create a study guide from this textbook page',
  maxTokens: 1200,
  temperature: 0.7
});

console.log(result.result);
console.log(`Credits used: ${result.creditsUsed}`);
```

##### getStatus()

Get account status and remaining credits.

**Returns:** Promise<{credits: number, user: any}>

**Example:**
```javascript
const status = await client.getStatus();
console.log(`Credits remaining: ${status.credits}`);
```

## Types

### VisionRequest

```typescript
interface VisionRequest {
  image: string;           // Base64 encoded image
  prompt: string;          // Analysis prompt
  maxTokens?: number;   // Maximum tokens (optional)
  temperature?: number;   // Response creativity 0-1 (optional)
}
```

### VisionResponse

```typescript
interface VisionResponse {
  success: boolean;        // Request success status
  result: string;         // Analysis result
  creditsUsed: number;     // Credits consumed
  remainingCredits: number; // Credits remaining
  processingTime: number;  // Processing time in ms
}
```

## Examples

### Basic Image Analysis

```javascript
const fs = require('fs');
const { EdPearClient } = require('@edpear/sdk');

const client = new EdPearClient({
  apiKey: process.env.EDPEAR_API_KEY
});

async function analyzeTextbook() {
  // Read image file
  const imageBuffer = fs.readFileSync('./textbook-page.jpg');
  const base64Image = imageBuffer.toString('base64');

  // Analyze image
  const result = await client.analyzeImage({
    image: base64Image,
    prompt: "Analyze this textbook page and create a study guide with key concepts, formulas, and practice questions."
  });

  console.log('Study Guide:');
  console.log(result.result);
  console.log(`\nCredits used: ${result.creditsUsed}`);
}
```

### Batch Processing

```javascript
async function analyzeMultiplePages(imagePaths, subject) {
  const results = [];
  
  for (const imagePath of imagePaths) {
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');
    
    const result = await client.analyzeImage({
      image: base64Image,
      prompt: `Analyze this ${subject} page and extract key concepts, formulas, and examples.`
    });
    
    results.push(result);
    
    // Add delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  return results;
}
```

### Error Handling

```javascript
async function safeAnalyze(image, prompt) {
  try {
    const result = await client.analyzeImage({ image, prompt });
    return result;
  } catch (error) {
    if (error.message.includes('Invalid API key')) {
      console.error('Please check your API key');
    } else if (error.message.includes('Insufficient credits')) {
      console.error('Please add more credits to your account');
    } else {
      console.error('Analysis failed:', error.message);
    }
    throw error;
  }
}
```

## Use Cases

### Educational Content Analysis

- **Textbook Pages**: Extract key concepts, formulas, and examples
- **Handwritten Notes**: Convert to structured, searchable content
- **Diagrams**: Analyze and explain complex diagrams
- **Charts**: Extract data and insights from educational charts

### Study Material Generation

- **Study Guides**: Create comprehensive study materials
- **Quiz Generation**: Generate questions from content
- **Summaries**: Create concise summaries of long content
- **Flashcards**: Generate flashcards from educational material

### Learning Assessment

- **Content Understanding**: Assess student understanding of material
- **Progress Tracking**: Track learning progress over time
- **Personalized Learning**: Adapt content to individual needs

## Best Practices

### Image Preparation

- Use high-quality images (minimum 300x300 pixels)
- Ensure good contrast and readability
- Avoid heavily compressed images
- Use standard formats (JPEG, PNG)

### Prompt Engineering

- Be specific about what you want analyzed
- Include context about the subject matter
- Ask for structured output when needed
- Use clear, educational language

### Rate Limiting

- Add delays between requests (1-2 seconds)
- Monitor your credit usage
- Use batch processing for multiple images
- Implement retry logic for failed requests

## Error Codes

| Error | Description | Solution |
|-------|-------------|----------|
| 401 | Invalid API key | Check your API key |
| 402 | Insufficient credits | Add credits to your account |
| 400 | Bad request | Check your request parameters |
| 429 | Rate limited | Reduce request frequency |
| 500 | Server error | Try again later |

## Support

- Documentation: [https://docs.edpear.com](https://docs.edpear.com)
- Support: [support@edpear.com](mailto:support@edpear.com)
- GitHub Issues: [https://github.com/edpear/sdk/issues](https://github.com/edpear/sdk/issues)
