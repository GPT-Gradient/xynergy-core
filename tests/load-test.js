/**
 * Load Testing Suite for XynergyOS Integration
 *
 * Uses Artillery.io for load testing
 * Install: npm install -g artillery
 * Run: artillery run tests/load-test.js
 */

module.exports = {
  config: {
    target: 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app',
    phases: [
      // Warm-up phase
      {
        duration: 60,
        arrivalRate: 5,
        name: 'Warm-up',
      },
      // Ramp-up phase
      {
        duration: 120,
        arrivalRate: 10,
        rampTo: 50,
        name: 'Ramp-up',
      },
      // Sustained load
      {
        duration: 300,
        arrivalRate: 50,
        name: 'Sustained load',
      },
      // Peak load
      {
        duration: 60,
        arrivalRate: 100,
        name: 'Peak load',
      },
      // Cool-down
      {
        duration: 60,
        arrivalRate: 10,
        name: 'Cool-down',
      },
    ],
    payload: {
      path: './test-data.csv',
      fields: ['auth_token'],
    },
    variables: {
      apiBaseUrl:
        'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app',
    },
    plugins: {
      metrics: {
        namespace: 'xynergyos_load_test',
      },
    },
    processor: './load-test-processor.js',
  },
  scenarios: [
    {
      name: 'Gateway Health Check',
      weight: 10,
      flow: [
        {
          get: {
            url: '/health',
            expect: [
              {
                statusCode: 200,
              },
              {
                contentType: 'json',
              },
            ],
          },
        },
      ],
    },
    {
      name: 'Slack Channels List',
      weight: 20,
      flow: [
        {
          get: {
            url: '/api/v2/slack/channels',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            expect: [
              {
                statusCode: [200, 401], // 401 if token invalid
              },
            ],
            capture: [
              {
                json: '$.data.channels[0].id',
                as: 'channelId',
              },
            ],
          },
        },
        {
          get: {
            url: '/api/v2/slack/channels/{{ channelId }}/messages',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            ifTrue: 'channelId',
          },
        },
      ],
    },
    {
      name: 'Calendar Events',
      weight: 20,
      flow: [
        {
          get: {
            url: '/api/v2/calendar/events',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            expect: [
              {
                statusCode: [200, 401],
              },
            ],
          },
        },
      ],
    },
    {
      name: 'Gmail Messages',
      weight: 20,
      flow: [
        {
          get: {
            url: '/api/v2/email/messages',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            expect: [
              {
                statusCode: [200, 401],
              },
            ],
          },
        },
      ],
    },
    {
      name: 'CRM Contacts',
      weight: 15,
      flow: [
        {
          get: {
            url: '/api/v2/crm/contacts',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            expect: [
              {
                statusCode: [200, 401],
              },
            ],
            capture: [
              {
                json: '$.data.contacts[0].id',
                as: 'contactId',
              },
            ],
          },
        },
        {
          get: {
            url: '/api/v2/crm/contacts/{{ contactId }}',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            ifTrue: 'contactId',
          },
        },
      ],
    },
    {
      name: 'Memory Items',
      weight: 10,
      flow: [
        {
          get: {
            url: '/api/v1/memory/items',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            expect: [
              {
                statusCode: [200, 401],
              },
            ],
          },
        },
      ],
    },
    {
      name: 'Research Sessions',
      weight: 5,
      flow: [
        {
          get: {
            url: '/api/v1/research-sessions',
            headers: {
              Authorization: 'Bearer {{ auth_token }}',
            },
            expect: [
              {
                statusCode: [200, 401],
              },
            ],
          },
        },
      ],
    },
  ],
};
