/**
 * WebSocket Test Client for XynergyOS Intelligence Gateway
 *
 * Usage:
 *   npm install -g tsx
 *   tsx tests/websocket-test-client.ts <firebase-token>
 */

import { io, Socket } from 'socket.io-client';

const GATEWAY_URL = process.env.GATEWAY_URL ||
  'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';

const WEBSOCKET_PATH = '/api/xynergyos/v2/stream';

class WebSocketTestClient {
  private socket: Socket | null = null;
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log(`\n🔌 Connecting to ${GATEWAY_URL}${WEBSOCKET_PATH}...`);

      this.socket = io(GATEWAY_URL, {
        path: WEBSOCKET_PATH,
        auth: {
          token: this.token,
        },
        transports: ['websocket', 'polling'],
      });

      // Connection events
      this.socket.on('connect', () => {
        console.log('✅ Connected successfully');
        console.log(`   Socket ID: ${this.socket?.id}`);
        resolve();
      });

      this.socket.on('connect_error', (error) => {
        console.error('❌ Connection error:', error.message);
        reject(error);
      });

      this.socket.on('disconnect', (reason) => {
        console.log(`\n🔌 Disconnected: ${reason}`);
      });

      this.socket.on('error', (error) => {
        console.error('❌ Socket error:', error);
      });

      // Custom events
      this.socket.on('subscribed', (data) => {
        console.log('✅ Subscribed to topics:', data.topics);
      });

      this.socket.on('unsubscribed', (data) => {
        console.log('✅ Unsubscribed from topics:', data.topics);
      });

      // Test message events
      this.socket.on('slack-message', (data) => {
        console.log('📨 Slack message received:', data);
      });

      this.socket.on('email-update', (data) => {
        console.log('📧 Email update received:', data);
      });

      this.socket.on('test-broadcast', (data) => {
        console.log('📢 Test broadcast received:', data);
      });
    });
  }

  subscribe(topics: string[]): void {
    if (!this.socket) {
      console.error('❌ Not connected');
      return;
    }

    console.log(`\n📡 Subscribing to topics: ${topics.join(', ')}`);
    this.socket.emit('subscribe', topics);
  }

  unsubscribe(topics: string[]): void {
    if (!this.socket) {
      console.error('❌ Not connected');
      return;
    }

    console.log(`\n📡 Unsubscribing from topics: ${topics.join(', ')}`);
    this.socket.emit('unsubscribe', topics);
  }

  disconnect(): void {
    if (this.socket) {
      console.log('\n🔌 Disconnecting...');
      this.socket.disconnect();
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

// Test script
async function runTests() {
  const token = process.argv[2];

  if (!token) {
    console.error('❌ Firebase token required');
    console.log('\nUsage: tsx tests/websocket-test-client.ts <firebase-token>');
    console.log('\nYou can get a Firebase token by:');
    console.log('1. Authenticating in your frontend');
    console.log('2. Calling firebase.auth().currentUser.getIdToken()');
    process.exit(1);
  }

  const client = new WebSocketTestClient(token);

  try {
    // Test 1: Connect
    console.log('\n🧪 Test 1: WebSocket Connection');
    await client.connect();
    await sleep(1000);

    // Test 2: Subscribe to topics
    console.log('\n🧪 Test 2: Subscribe to Topics');
    client.subscribe(['slack-messages', 'email-updates', 'calendar-events']);
    await sleep(2000);

    // Test 3: Keep connection alive
    console.log('\n🧪 Test 3: Connection Stability (10 seconds)');
    console.log('   Waiting for any incoming messages...');
    await sleep(10000);

    // Test 4: Unsubscribe
    console.log('\n🧪 Test 4: Unsubscribe from Topics');
    client.unsubscribe(['email-updates']);
    await sleep(2000);

    // Test 5: Disconnect
    console.log('\n🧪 Test 5: Graceful Disconnect');
    client.disconnect();
    await sleep(1000);

    console.log('\n✅ All tests completed successfully!\n');
  } catch (error) {
    console.error('\n❌ Test failed:', error);
    process.exit(1);
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run tests if called directly
if (require.main === module) {
  runTests().catch(console.error);
}

export { WebSocketTestClient };
