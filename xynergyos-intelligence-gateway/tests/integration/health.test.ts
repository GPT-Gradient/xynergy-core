/**
 * Integration tests for health check endpoints
 *
 * Run with: npm test
 */

import axios from 'axios';

const GATEWAY_URL = process.env.GATEWAY_URL ||
  'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';

describe('Health Check Endpoints', () => {
  describe('GET /health', () => {
    it('should return 200 OK', async () => {
      const response = await axios.get(`${GATEWAY_URL}/health`);
      expect(response.status).toBe(200);
    });

    it('should return correct health status', async () => {
      const response = await axios.get(`${GATEWAY_URL}/health`);
      expect(response.data).toHaveProperty('status', 'healthy');
      expect(response.data).toHaveProperty('service', 'xynergyos-intelligence-gateway');
      expect(response.data).toHaveProperty('version');
      expect(response.data).toHaveProperty('timestamp');
    });

    it('should include request ID in response headers', async () => {
      const response = await axios.get(`${GATEWAY_URL}/health`);
      expect(response.headers).toHaveProperty('x-request-id');
    });
  });

  describe('GET /health/deep', () => {
    it('should return 200 OK when all services healthy', async () => {
      const response = await axios.get(`${GATEWAY_URL}/health/deep`);
      expect(response.status).toBe(200);
    });

    it('should check Firestore connectivity', async () => {
      const response = await axios.get(`${GATEWAY_URL}/health/deep`);
      expect(response.data.checks).toHaveProperty('firestore');
      expect(response.data.checks.firestore).toBe('healthy');
    });

    it('should report service configuration status', async () => {
      const response = await axios.get(`${GATEWAY_URL}/health/deep`);
      expect(response.data.checks).toHaveProperty('services');
      expect(response.data.checks.services).toHaveProperty('aiRouting');
    });
  });

  describe('GET /api/v1/health', () => {
    it('should respond on versioned endpoint', async () => {
      const response = await axios.get(`${GATEWAY_URL}/api/v1/health`);
      expect(response.status).toBe(200);
      expect(response.data.status).toBe('healthy');
    });
  });
});

describe('Rate Limiting', () => {
  it('should include rate limit headers', async () => {
    const response = await axios.get(`${GATEWAY_URL}/health`);
    expect(response.headers).toHaveProperty('ratelimit-limit');
    expect(response.headers).toHaveProperty('ratelimit-remaining');
  });
});

describe('CORS Headers', () => {
  it('should include CORS headers', async () => {
    const response = await axios.get(`${GATEWAY_URL}/health`);
    expect(response.headers).toHaveProperty('access-control-allow-origin');
  });
});

describe('Error Handling', () => {
  it('should return 404 for non-existent routes', async () => {
    try {
      await axios.get(`${GATEWAY_URL}/nonexistent`);
      fail('Should have thrown 404 error');
    } catch (error: any) {
      expect(error.response.status).toBe(404);
      expect(error.response.data).toHaveProperty('error', 'Not Found');
    }
  });
});
