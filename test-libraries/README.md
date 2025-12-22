# EdPear Libraries Test Suite

This folder contains test scripts to verify that both the EdPear CLI and SDK are working correctly.

## Setup

1. **Install dependencies:**
   ```bash
   cd test-libraries
   npm install
   ```

2. **Install CLI globally (if not already installed):**
   ```bash
   npm install -g @edpear/cli
   ```

## Running Tests

### Test CLI Only
```bash
npm run test:cli
```

This tests:
- ✅ CLI is installed globally
- ✅ CLI help command works
- ✅ CLI config directory structure
- ✅ All CLI commands are available
- ✅ CLI status command

### Test SDK Only
```bash
npm run test:sdk
```

This tests:
- ✅ SDK package is installed
- ✅ SDK exports are correct
- ✅ EdPearClient can be instantiated
- ✅ createEdPearClient helper works
- ✅ Client configuration is correct
- ✅ Client works with environment variables
- ✅ Client handles missing API key gracefully

### Test SDK with API Calls
```bash
# Set your API key
export EDPEAR_API_KEY=your_api_key_here

# Or on Windows PowerShell:
$env:EDPEAR_API_KEY="your_api_key_here"

# Run the API test
node test-sdk-api.js
```

This tests:
- ✅ Get account status
- ✅ Analyze image API call

### Test Full Workflow (Recommended)
```bash
npm run test:workflow
```

This comprehensive test simulates the complete workflow:
- User registration/login
- API key generation
- SDK usage
- API calls with credit tracking
- Database verification

### Test Everything
```bash
npm run test:all
```

## Test Results

Tests will show:
- ✅ **PASSED** - Test completed successfully
- ❌ **FAILED** - Test failed with error message
- ⚠️ **WARNING** - Test passed but with warnings (e.g., user not logged in)

## Expected Behavior

### CLI Tests
- If you haven't logged in with `edpear login`, some tests may show warnings but still pass
- This is expected behavior

### SDK Tests
- Basic tests don't require an API key
- API tests require a valid `EDPEAR_API_KEY` environment variable
- API tests require your API to be running and accessible

## Troubleshooting

### CLI not found
```bash
npm install -g @edpear/cli
```

### SDK not found
```bash
npm install @edpear/sdk
```

### API tests failing
- Make sure `EDPEAR_API_KEY` is set correctly
- Make sure your API is running and accessible
- Check that you have credits in your account

## Full Workflow Test

The `test-full-workflow.js` script simulates the complete user journey:

1. **User Registration** - Creates a test user account
2. **Authentication** - Logs in and gets JWT token
3. **API Key Generation** - Creates a new API key for the user
4. **API Key Listing** - Lists all keys for the user
5. **SDK Integration** - Tests SDK with generated API key
6. **API Calls** - Makes actual API calls and tracks usage
7. **Database Verification** - Verifies keys are stored and tracked correctly

### Run Full Workflow Test
```bash
npm run test:workflow
```

**Note:** Make sure your API is running at `http://localhost:3000` (or set `EDPEAR_API_URL` environment variable).

## Manual Testing

### Test CLI Manually
```bash
# Check version
edpear --version

# See help
edpear --help

# Check status
edpear status

# Login (opens browser)
edpear login

# Generate API key
edpear generate-key
```

### Test SDK Manually
Create a test file `manual-test.js`:

```javascript
import { EdPearClient } from '@edpear/sdk';

const client = new EdPearClient({
  apiKey: process.env.EDPEAR_API_KEY
});

// Test getStatus
const status = await client.getStatus();
console.log('Status:', status);

// Test analyzeImage
const result = await client.analyzeImage({
  image: 'base64_image_here',
  prompt: 'Analyze this image'
});
console.log('Result:', result);
```

Run it:
```bash
EDPEAR_API_KEY=your_key node manual-test.js
```
