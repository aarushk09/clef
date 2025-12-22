#!/usr/bin/env node

/**
 * Test script for EdPear SDK API calls
 * This requires a valid API key and actual API endpoint
 * 
 * Usage:
 *   EDPEAR_API_KEY=your_key node test-sdk-api.js
 */

import { EdPearClient } from '@edpear/sdk';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

console.log('🧪 Testing EdPear SDK API Calls\n');
console.log('='.repeat(50));

const apiKey = process.env.EDPEAR_API_KEY;

if (!apiKey) {
  console.log('❌ EDPEAR_API_KEY environment variable not set');
  console.log('   Set it with: export EDPEAR_API_KEY=your_key');
  console.log('   Or: $env:EDPEAR_API_KEY="your_key" (PowerShell)');
  process.exit(1);
}

const client = new EdPearClient({ apiKey });

async function testAPI() {
  const tests = [];
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    tests.push({ name, fn });
  }

  // Test 1: Get account status
  test('Get account status', async () => {
    try {
      const status = await client.getStatus();
      console.log(`   Credits: ${status.credits}`);
      console.log(`   User: ${status.user?.name || 'N/A'}`);
    } catch (error) {
      if (error.message.includes('Invalid API key')) {
        throw new Error('Invalid API key - check your EDPEAR_API_KEY');
      }
      throw error;
    }
  });

  // Test 2: Analyze a test image (if you have one)
  test('Analyze image (test)', async () => {
    try {
      // Create a minimal test image (1x1 red pixel in base64)
      const testImage = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
      
      const result = await client.analyzeImage({
        image: testImage,
        prompt: 'What color is this image?',
        maxTokens: 50
      });
      
      console.log(`   Result: ${result.result.substring(0, 100)}...`);
      console.log(`   Credits used: ${result.creditsUsed}`);
    } catch (error) {
      if (error.message.includes('Invalid API key')) {
        throw new Error('Invalid API key');
      } else if (error.message.includes('Insufficient credits')) {
        throw new Error('Insufficient credits - add credits to your account');
      } else {
        console.log(`   ⚠️  API call failed: ${error.message}`);
        throw error;
      }
    }
  });

  // Run tests
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
    console.log('🎉 All API tests passed!\n');
  } else {
    console.log('⚠️  Some API tests failed\n');
  }
}

testAPI().catch(console.error);
