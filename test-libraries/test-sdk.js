#!/usr/bin/env node

/**
 * Test script for EdPear SDK
 * This tests the SDK installation and basic functionality
 */

// Dynamic imports are used in each test

console.log('🧪 Testing EdPear SDK\n');
console.log('='.repeat(50));

const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  tests.push({ name, fn });
}

async function runTests() {
  for (const { name, fn } of tests) {
    try {
      console.log(`\n📋 Test: ${name}`);
      await fn();
      console.log(`✅ PASSED: ${name}`);
      passed++;
    } catch (error) {
      console.log(`❌ FAILED: ${name}`);
      console.log(`   Error: ${error.message}`);
      failed++;
    }
  }

  console.log('\n' + '='.repeat(50));
  console.log(`\n📊 Test Results:`);
  console.log(`   ✅ Passed: ${passed}`);
  console.log(`   ❌ Failed: ${failed}`);
  console.log(`   📈 Total: ${tests.length}\n`);

  if (failed === 0) {
    console.log('🎉 All tests passed!\n');
    process.exit(0);
  } else {
    console.log('⚠️  Some tests failed\n');
    process.exit(1);
  }
}

// Test 1: Check if SDK is installed
test('SDK package is installed', async () => {
  try {
    const sdk = await import('@edpear/sdk');
    if (!sdk.EdPearClient) {
      throw new Error('EdPearClient not found in SDK');
    }
    console.log('   SDK package found');
  } catch (error) {
    throw new Error('SDK not installed. Run: npm install @edpear/sdk');
  }
});

// Test 2: Test SDK imports
test('SDK exports are correct', async () => {
  try {
    const { EdPearClient, createEdPearClient } = await import('@edpear/sdk');
    
    if (typeof EdPearClient !== 'function') {
      throw new Error('EdPearClient is not a function');
    }
    
    if (typeof createEdPearClient !== 'function') {
      throw new Error('createEdPearClient is not a function');
    }
    
    console.log('   All exports are correct');
  } catch (error) {
    throw error;
  }
});

// Test 3: Test EdPearClient instantiation
test('EdPearClient can be instantiated', async () => {
  try {
    const { EdPearClient } = await import('@edpear/sdk');
    const apiKey = process.env.EDPEAR_API_KEY || 'test-key-123';
    const client = new EdPearClient({ apiKey });
    
    if (!client) {
      throw new Error('Failed to create client instance');
    }
    
    console.log('   Client instance created successfully');
  } catch (error) {
    throw error;
  }
});

// Test 4: Test createEdPearClient helper
test('createEdPearClient helper works', async () => {
  try {
    const { createEdPearClient } = await import('@edpear/sdk');
    const apiKey = process.env.EDPEAR_API_KEY || 'test-key-123';
    const client = createEdPearClient(apiKey);
    
    if (!client) {
      throw new Error('Failed to create client with helper');
    }
    
    console.log('   Helper function works');
  } catch (error) {
    throw error;
  }
});

// Test 5: Test client configuration
test('Client configuration is correct', async () => {
  try {
    const { EdPearClient } = await import('@edpear/sdk');
    const apiKey = 'test-api-key';
    const customBaseURL = 'https://custom-api.example.com';
    const client = new EdPearClient({ apiKey, baseURL: customBaseURL });
    
    // We can't directly access private properties, but we can test methods exist
    if (typeof client.analyzeImage !== 'function') {
      throw new Error('analyzeImage method not found');
    }
    
    if (typeof client.getStatus !== 'function') {
      throw new Error('getStatus method not found');
    }
    
    console.log('   Client methods are available');
  } catch (error) {
    throw error;
  }
});

// Test 6: Test with environment variable
test('Client works with environment variable', async () => {
  try {
    const { EdPearClient } = await import('@edpear/sdk');
    // This test just checks if it doesn't throw with env var
    const apiKey = process.env.EDPEAR_API_KEY || 'env-test-key';
    const client = new EdPearClient({ apiKey });
    console.log('   Client works with environment variables');
  } catch (error) {
    throw error;
  }
});

// Test 7: Test error handling (without actual API call)
test('Client handles missing API key gracefully', async () => {
  try {
    const { EdPearClient } = await import('@edpear/sdk');
    // This should not throw during instantiation
    const client = new EdPearClient({ apiKey: '' });
    console.log('   Client handles empty API key');
  } catch (error) {
    // If it throws, that's also acceptable behavior
    if (error.message.includes('API key')) {
      console.log('   Client validates API key (expected behavior)');
    } else {
      throw error;
    }
  }
});

console.log('\n🚀 Starting SDK tests...\n');
runTests().catch(console.error);
