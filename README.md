# EdPear - AI-Powered Educational Components

Professional AI components for educational technology applications. Build smarter learning experiences with our vision AI and component library.

## 🚀 Features

- **Vision AI**: Advanced image analysis for educational content, textbooks, and learning materials
- **Easy Integration**: Simple API calls and CLI tools to integrate AI into your applications
- **Secure & Reliable**: Enterprise-grade security with usage tracking and credit management
- **Developer-First**: Comprehensive SDK and CLI tools for seamless integration

## 📦 Installation

### CLI Tool
```bash
npm install -g @edpear/cli
```

### SDK
```bash
npm install @edpear/sdk
```

## 🛠️ Quick Start

### 1. Install CLI and Login
```bash
# Install the CLI globally
npm install -g @edpear/cli

# Login to your account
edpear login
```

### 2. Generate API Key
```bash
# Generate a new API key
edpear generate-key

# Check your status
edpear status
```

### 3. Use in Your Code
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

## 🔧 CLI Commands

| Command | Description |
|---------|-------------|
| `edpear login` | Authenticate with EdPear |
| `edpear generate-key` | Generate a new API key |
| `edpear status` | Show current status and API keys |
| `edpear logout` | Logout from EdPear |

## 📚 API Reference

### Vision Analysis

Analyze educational images with our specialized AI model.

```javascript
const result = await client.analyzeImage({
  image: 'base64-encoded-image',
  prompt: 'Your analysis prompt',
  maxTokens: 1000,        // Optional
  temperature: 0.7        // Optional
});
```

**Response:**
```javascript
{
  success: true,
  result: "Analysis result...",
  creditsUsed: 5,
  remainingCredits: 95,
  processingTime: 1200
}
```

### Account Status

Check your account information and remaining credits.

```javascript
const status = await client.getStatus();
```

## 🎯 Use Cases

- **Textbook Analysis**: Extract key concepts from textbook pages
- **Handwritten Notes**: Convert handwritten notes to structured content
- **Study Guides**: Generate comprehensive study materials
- **Educational Content**: Analyze diagrams, charts, and educational images
- **Learning Assessment**: Create quizzes and assessments from content

## 🔒 Security

- All API keys are securely stored and encrypted
- Requests are proxied through our secure infrastructure
- Usage tracking and rate limiting
- No direct access to underlying AI models

## 📊 Dashboard

Access your dashboard at [https://edpear.com/dashboard](https://edpear.com/dashboard) to:

- View usage statistics
- Manage API keys
- Monitor credit usage
- Access documentation

## 🛡️ Privacy

- Your data is never stored permanently
- Images are processed and immediately discarded
- All requests are logged for usage tracking only
- No personal information is shared with third parties

## 📞 Support

- Documentation: [https://docs.edpear.com](https://docs.edpear.com)
- Support: [support@edpear.com](mailto:support@edpear.com)
- GitHub: [https://github.com/edpear](https://github.com/edpear)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

Built with ❤️ for the educational technology community.