#!/usr/bin/env node

/**
 * Test script for EdPear CLI
 * This tests the CLI installation and basic functionality
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

console.log('🧪 Testing EdPear CLI\n');
console.log('='.repeat(50));

const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  tests.push({ name, fn });
}

function runTests() {
  tests.forEach(({ name, fn }) => {
    try {
      console.log(`\n📋 Test: ${name}`);
      fn();
      console.log(`✅ PASSED: ${name}`);
      passed++;
    } catch (error) {
      console.log(`❌ FAILED: ${name}`);
      console.log(`   Error: ${error.message}`);
      failed++;
    }
  });

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

// Test 1: Check if CLI is installed globally
test('CLI is installed globally', () => {
  try {
    const version = execSync('edpear --version', { encoding: 'utf-8', stdio: 'pipe' });
    console.log(`   Version: ${version.trim()}`);
  } catch (error) {
    throw new Error('CLI not found. Install with: npm install -g @edpear/cli');
  }
});

// Test 2: Check if CLI help command works
test('CLI help command works', () => {
  try {
    const help = execSync('edpear --help', { encoding: 'utf-8', stdio: 'pipe' });
    if (!help.includes('EdPear CLI')) {
      throw new Error('Help output does not contain expected text');
    }
    console.log('   Help command works');
  } catch (error) {
    throw new Error('Help command failed');
  }
});

// Test 3: Check if CLI config directory exists (after login)
test('CLI config directory structure', () => {
  const configDir = join(homedir(), '.edpear');
  const configFile = join(configDir, 'config.json');
  
  if (existsSync(configDir)) {
    console.log(`   Config directory exists: ${configDir}`);
    if (existsSync(configFile)) {
      console.log(`   Config file exists: ${configFile}`);
    } else {
      console.log('   ⚠️  Config file not found (user may not be logged in)');
    }
  } else {
    console.log('   ⚠️  Config directory not found (user may not be logged in)');
  }
});

// Test 4: Check CLI commands are available
test('CLI commands are available', () => {
  const commands = ['login', 'generate-key', 'status', 'logout'];
  const help = execSync('edpear --help', { encoding: 'utf-8', stdio: 'pipe' });
  
  commands.forEach(cmd => {
    if (!help.includes(cmd)) {
      throw new Error(`Command '${cmd}' not found in help`);
    }
  });
  console.log(`   All commands available: ${commands.join(', ')}`);
});

// Test 5: Test CLI status command (may fail if not logged in, that's OK)
test('CLI status command', () => {
  try {
    const status = execSync('edpear status', { encoding: 'utf-8', stdio: 'pipe' });
    console.log('   Status command works (user is logged in)');
  } catch (error) {
    if (error.message.includes('Not authenticated')) {
      console.log('   Status command works (user not logged in - expected)');
    } else {
      throw error;
    }
  }
});

console.log('\n🚀 Starting CLI tests...\n');
runTests();
