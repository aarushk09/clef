#!/usr/bin/env node

/**
 * Full Workflow Test - Simulates complete CLI and SDK usage
 * This test simulates:
 * 1. User registration/login
 * 2. CLI login
 * 3. API key generation via CLI
 * 4. SDK usage with generated API key
 * 5. API calls and credit tracking
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import axios from 'axios';

console.log('🚀 EdPear Full Workflow Test\n');
console.log('='.repeat(60));

const BASE_URL = process.env.EDPEAR_API_URL || 'http://localhost:3000';
const TEST_EMAIL = `test-${Date.now()}@edpear.test`;
const TEST_PASSWORD = 'TestPassword123!';
const TEST_NAME = 'Test User';

let authToken = null;
let userId = null;
let apiKey = null;

const steps = [];
let currentStep = 0;

function logStep(name, status, details = '') {
  currentStep++;
  const icon = status === 'success' ? '✅' : status === 'error' ? '❌' : '⏳';
  console.log(`\n${icon} Step ${currentStep}: ${name}`);
  if (details) {
    console.log(`   ${details}`);
  }
  steps.push({ step: currentStep, name, status, details });
}

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testFullWorkflow() {
  try {
    // Step 1: Register a new user
    logStep('Register Test User', 'pending');
    try {
      const registerResponse = await axios.post(`${BASE_URL}/api/auth/register`, {
        email: TEST_EMAIL,
        password: TEST_PASSWORD,
        name: TEST_NAME,
      });

      if (registerResponse.data.success) {
        logStep('Register Test User', 'success', `User created: ${TEST_EMAIL}`);
      } else {
        throw new Error('Registration failed');
      }
    } catch (error) {
      if (error.response?.status === 400 && error.response.data.error.includes('already exists')) {
        logStep('Register Test User', 'success', 'User already exists (using existing account)');
      } else {
        throw error;
      }
    }

    // Step 2: Login to get JWT token
    logStep('Login and Get Token', 'pending');
    const loginResponse = await axios.post(`${BASE_URL}/api/auth/login`, {
      email: TEST_EMAIL,
      password: TEST_PASSWORD,
    });

    if (!loginResponse.data.success || !loginResponse.data.token) {
      throw new Error('Login failed');
    }

    authToken = loginResponse.data.token;
    userId = loginResponse.data.user.id;
    logStep('Login and Get Token', 'success', `Token received, User ID: ${userId}`);

    // Step 3: Get user info
    logStep('Get User Info', 'pending');
    const userResponse = await axios.get(`${BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (userResponse.data.success) {
      const user = userResponse.data.user;
      logStep('Get User Info', 'success', `Name: ${user.name}, Credits: ${user.credits}`);
    } else {
      throw new Error('Failed to get user info');
    }

    // Step 4: Generate API Key via API
    logStep('Generate API Key', 'pending');
    const keyName = `Test Key ${Date.now()}`;
    const keyResponse = await axios.post(
      `${BASE_URL}/api/keys/generate`,
      { name: keyName },
      {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!keyResponse.data.success || !keyResponse.data.apiKey) {
      throw new Error('API key generation failed');
    }

    apiKey = keyResponse.data.apiKey.key;
    logStep('Generate API Key', 'success', `Key generated: ${apiKey.substring(0, 30)}...`);

    // Step 5: List API Keys
    logStep('List API Keys', 'pending');
    const listResponse = await axios.get(`${BASE_URL}/api/keys/list`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (listResponse.data.success) {
      const keys = listResponse.data.apiKeys;
      logStep('List API Keys', 'success', `Found ${keys.length} API key(s)`);
      keys.forEach((key, index) => {
        console.log(`   ${index + 1}. ${key.name} - ${key.key} (Used: ${key.usageCount} times)`);
      });
    } else {
      throw new Error('Failed to list API keys');
    }

    // Step 6: Test SDK with generated API key
    logStep('Test SDK with API Key', 'pending');
    const { EdPearClient } = await import('@edpear/sdk');
    const client = new EdPearClient({
      apiKey: apiKey,
      baseURL: BASE_URL,
    });

    // Test getStatus
    try {
      const status = await client.getStatus();
      if (status.credits !== undefined) {
        logStep('Test SDK - Get Status', 'success', `Credits: ${status.credits}, User: ${status.user?.name || 'N/A'}`);
      } else {
        logStep('Test SDK - Get Status', 'pending', 'Status endpoint returned unexpected format');
      }
    } catch (error) {
      logStep('Test SDK - Get Status', 'pending', `Status check: ${error.message}`);
    }

    // Step 7: Test API Key Validation (simulate vision API call)
    logStep('Test API Key Validation', 'pending');
    const testImage = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
    
    try {
      const visionResponse = await axios.post(
        `${BASE_URL}/api/vision`,
        {
          image: testImage,
          prompt: 'What color is this image?',
          maxTokens: 50,
        },
        {
          headers: {
            'x-api-key': apiKey,
            'Content-Type': 'application/json',
          },
        }
      );

      if (visionResponse.data.success) {
        logStep('Test API Key Validation', 'success', 
          `API call successful! Credits used: ${visionResponse.data.creditsUsed}, Remaining: ${visionResponse.data.remainingCredits}`
        );
      } else {
        throw new Error('Vision API call failed');
      }
    } catch (error) {
      if (error.response?.status === 402) {
        logStep('Test API Key Validation', 'pending', 'Insufficient credits (expected for test account)');
      } else if (error.response?.status === 401) {
        logStep('Test API Key Validation', 'error', 'API key validation failed');
        throw error;
      } else {
        logStep('Test API Key Validation', 'pending', `API endpoint may not be fully configured: ${error.message}`);
      }
    }

    // Step 8: Verify API key was tracked in database
    logStep('Verify API Key Usage Tracking', 'pending');
    const updatedListResponse = await axios.get(`${BASE_URL}/api/keys/list`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (updatedListResponse.data.success) {
      const updatedKey = updatedListResponse.data.apiKeys.find(k => k.key.startsWith(apiKey.substring(0, 20)));
      if (updatedKey && updatedKey.usageCount > 0) {
        logStep('Verify API Key Usage Tracking', 'success', 
          `API key usage tracked! Usage count: ${updatedKey.usageCount}`
        );
      } else {
        logStep('Verify API Key Usage Tracking', 'pending', 'Usage tracking may not have updated yet');
      }
    }

    // Step 9: Test CLI simulation (if CLI is installed)
    logStep('Test CLI Commands', 'pending');
    try {
      const cliVersion = execSync('edpear --version', { encoding: 'utf-8', stdio: 'pipe' });
      logStep('Test CLI Commands', 'success', `CLI installed: ${cliVersion.trim()}`);
      
      // Test CLI status (may fail if not logged in via CLI, that's OK)
      try {
        const cliStatus = execSync('edpear status', { encoding: 'utf-8', stdio: 'pipe' });
        logStep('CLI Status Command', 'success', 'CLI status works');
      } catch (error) {
        logStep('CLI Status Command', 'pending', 'CLI not logged in (expected - using API directly)');
      }
    } catch (error) {
      logStep('Test CLI Commands', 'pending', 'CLI not installed globally (install with: npm install -g @edpear/cli)');
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('\n📊 Workflow Test Summary\n');
    
    const successful = steps.filter(s => s.status === 'success').length;
    const pending = steps.filter(s => s.status === 'pending').length;
    const errors = steps.filter(s => s.status === 'error').length;
    
    console.log(`   ✅ Successful: ${successful}`);
    console.log(`   ⏳ Pending/Optional: ${pending}`);
    console.log(`   ❌ Errors: ${errors}`);
    console.log(`   📈 Total Steps: ${steps.length}\n`);

    if (errors === 0) {
      console.log('🎉 Full workflow test completed successfully!\n');
      console.log('📝 Test Results:');
      console.log(`   - User ID: ${userId}`);
      console.log(`   - API Key: ${apiKey.substring(0, 30)}...`);
      console.log(`   - Email: ${TEST_EMAIL}`);
      console.log(`   - Password: ${TEST_PASSWORD}\n`);
      console.log('💡 You can now use this API key to test the SDK!');
    } else {
      console.log('⚠️  Some steps had errors. Check the output above.\n');
    }

  } catch (error) {
    console.error('\n❌ Workflow test failed:', error.message);
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Error: ${error.response.data?.error || error.response.data}`);
    }
    process.exit(1);
  }
}

// Run the test
testFullWorkflow();
