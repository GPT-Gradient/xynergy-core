#!/usr/bin/env node

/**
 * JWT Token Generator and Tester
 *
 * This script generates a test JWT token and tests authentication
 * with the Intelligence Gateway.
 *
 * Usage:
 *   node test-jwt-auth.js
 */

const jwt = require('jsonwebtoken');
const https = require('https');

// JWT Secret (same as in xynergyos-backend)
const JWT_SECRET = '8f4a9e2b7c1d5f3a6e8b9c4d2f7a1e5b3c6d8f4a9e2b7c1d5f3a6e8b9c4d2f7a';

// Generate a test JWT token
const payload = {
  user_id: 'test-user-123',
  tenant_id: 'clearforge',
  email: 'test@example.com',
  roles: ['admin'],
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + (60 * 60 * 24) // 24 hours
};

const token = jwt.sign(payload, JWT_SECRET);

console.log('='.repeat(80));
console.log('JWT AUTHENTICATION TEST');
console.log('='.repeat(80));
console.log('\n📝 Generated JWT Token:');
console.log(token);
console.log('\n📦 Token Payload:');
console.log(JSON.stringify(payload, null, 2));
console.log('\n' + '='.repeat(80));

// Test the token with the Intelligence Gateway
console.log('\n🔍 Testing Authentication with Intelligence Gateway...\n');

const testEndpoints = [
  '/health',
  '/api/v1/health',
  '/api/v2/crm/statistics',
  '/api/v2/slack/channels',
];

async function testEndpoint(path, useAuth = false) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'xynergy-intelligence-gateway-835612502919.us-central1.run.app',
      port: 443,
      path: path,
      method: 'GET',
      headers: useAuth ? {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      } : {},
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: data
        });
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.end();
  });
}

async function runTests() {
  console.log('Testing endpoints:\n');

  // Test health endpoint (no auth)
  try {
    console.log('1️⃣  GET /health (no auth)');
    const result = await testEndpoint('/health', false);
    console.log(`   Status: ${result.status}`);
    console.log(`   Response: ${result.body.substring(0, 100)}...`);
    console.log('   ✅ SUCCESS\n');
  } catch (error) {
    console.log('   ❌ FAILED:', error.message, '\n');
  }

  // Test authenticated endpoints
  for (const endpoint of ['/api/v2/crm/statistics', '/api/v2/slack/channels']) {
    try {
      console.log(`2️⃣  GET ${endpoint} (with JWT auth)`);
      const result = await testEndpoint(endpoint, true);
      console.log(`   Status: ${result.status}`);

      if (result.status === 200) {
        console.log('   ✅ JWT AUTHENTICATION WORKING!');
        try {
          const json = JSON.parse(result.body);
          console.log(`   Response preview: ${JSON.stringify(json).substring(0, 100)}...`);
        } catch (e) {
          console.log(`   Response: ${result.body.substring(0, 100)}...`);
        }
      } else if (result.status === 401) {
        console.log('   ❌ Authentication failed - JWT not working');
        console.log(`   Error: ${result.body}`);
      } else if (result.status === 503) {
        console.log('   ⚠️  Backend service unavailable (but auth worked!)');
      } else {
        console.log(`   ⚠️  Unexpected status: ${result.status}`);
        console.log(`   Response: ${result.body.substring(0, 200)}`);
      }
      console.log('');
    } catch (error) {
      console.log('   ❌ FAILED:', error.message, '\n');
    }
  }

  console.log('='.repeat(80));
  console.log('TEST COMPLETE');
  console.log('='.repeat(80));
  console.log('\n💡 How to use this token in curl:\n');
  console.log(`curl -H "Authorization: Bearer ${token}" \\`);
  console.log(`  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/crm/statistics\n`);
}

runTests().catch(console.error);
