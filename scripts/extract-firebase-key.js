#!/usr/bin/env node

/**
 * Helper script to extract Firebase Admin credentials from JSON file
 * Usage: node scripts/extract-firebase-key.js path/to/service-account-key.json
 */

const fs = require('fs');
const path = require('path');

const jsonPath = process.argv[2];

if (!jsonPath) {
  console.error('❌ Please provide the path to your Firebase service account JSON file');
  console.log('\nUsage: node scripts/extract-firebase-key.js path/to/service-account-key.json');
  process.exit(1);
}

if (!fs.existsSync(jsonPath)) {
  console.error(`❌ File not found: ${jsonPath}`);
  process.exit(1);
}

try {
  const jsonContent = fs.readFileSync(jsonPath, 'utf8');
  const serviceAccount = JSON.parse(jsonContent);

  console.log('\n📋 Add these to your .env.local file:\n');
  console.log('='.repeat(60));
  console.log(`FIREBASE_ADMIN_PROJECT_ID=${serviceAccount.project_id}`);
  console.log(`FIREBASE_ADMIN_CLIENT_EMAIL=${serviceAccount.client_email}`);
  console.log(`FIREBASE_ADMIN_PRIVATE_KEY="${serviceAccount.private_key}"`);
  console.log('='.repeat(60));
  console.log('\n✅ Copy the above lines to your .env.local file');
  console.log('⚠️  Make sure to keep the quotes around the private key!\n');

} catch (error) {
  console.error('❌ Error reading JSON file:', error.message);
  console.error('\n💡 Make sure the file is a valid Firebase service account JSON file');
  process.exit(1);
}
