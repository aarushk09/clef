#!/usr/bin/env node

/**
 * Helper script to generate secure random secrets for EdPear
 * Usage: node scripts/generate-secrets.js
 */

const crypto = require('crypto');

console.log('\n🔐 EdPear Secret Generator\n');
console.log('='.repeat(50));

// Generate NextAuth Secret
const nextAuthSecret = crypto.randomBytes(32).toString('base64');
console.log('\n📝 NextAuth Secret:');
console.log(`NEXTAUTH_SECRET=${nextAuthSecret}`);

// Generate JWT Secret (different from NextAuth)
const jwtSecret = crypto.randomBytes(32).toString('base64');
console.log('\n🔑 JWT Secret:');
console.log(`JWT_SECRET=${jwtSecret}`);

console.log('\n' + '='.repeat(50));
console.log('\n✅ Copy these values to your .env.local file');
console.log('⚠️  Keep these secrets secure and never commit them to git!\n');
