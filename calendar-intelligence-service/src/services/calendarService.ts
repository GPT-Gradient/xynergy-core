import { google } from 'googleapis';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';
import { ServiceUnavailableError } from '../middleware/errorHandler';

/**
 * Calendar Service - Manages Google Calendar API interactions
 * NOTE: This service uses mock data when Calendar credentials are not configured
 */
export class CalendarService {
  private calendar: any = null;
  private oauth2Client: any = null;
  private isMockMode: boolean = false;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    if (appConfig.calendar.clientId && appConfig.calendar.clientSecret) {
      try {
        this.oauth2Client = new google.auth.OAuth2(
          appConfig.calendar.clientId,
          appConfig.calendar.clientSecret,
          appConfig.calendar.redirectUri
        );
        this.isMockMode = false;
        logger.info('Calendar OAuth client initialized');
      } catch (error) {
        logger.error('Failed to initialize Calendar OAuth client', { error });
        this.isMockMode = true;
      }
    } else {
      logger.warn('Calendar credentials not configured - running in MOCK MODE');
      this.isMockMode = true;
    }
  }

  /**
   * Set access token for user
   * This should be called with the user's OAuth access token
   */
  public setAccessToken(accessToken: string): void {
    if (!this.oauth2Client) {
      throw new ServiceUnavailableError('OAuth client not initialized');
    }
    this.oauth2Client.setCredentials({ access_token: accessToken });
    this.calendar = google.calendar({ version: 'v3', auth: this.oauth2Client });
  }

  /**
   * Check if service is in mock mode
   */
  public isInMockMode(): boolean {
    return this.isMockMode;
  }

  /**
   * Test Calendar API connection
   */
  async testConnection(): Promise<{ ok: boolean; calendar?: string; error?: string }> {
    if (this.isMockMode) {
      return {
        ok: true,
        calendar: 'Mock Calendar (No credentials configured)',
      };
    }

    try {
      const calendarList = await this.calendar.calendarList.list({ maxResults: 1 });
      return {
        ok: true,
        calendar: calendarList.data.items?.[0]?.summary || 'Calendar',
      };
    } catch (error: any) {
      logger.error('Calendar connection test failed', { error: error.message });
      return {
        ok: false,
        error: error.message,
      };
    }
  }

  /**
   * List calendar events
   */
  async listEvents(
    timeMin?: Date,
    timeMax?: Date,
    maxResults: number = 50
  ): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockEvents(maxResults);
    }

    try {
      const response = await this.calendar.events.list({
        calendarId: 'primary',
        timeMin: (timeMin || new Date()).toISOString(),
        timeMax: timeMax?.toISOString(),
        maxResults,
        singleEvents: true,
        orderBy: 'startTime',
      });

      return response.data.items || [];
    } catch (error: any) {
      logger.error('Failed to list calendar events', { error: error.message });
      throw new ServiceUnavailableError('Failed to fetch calendar events');
    }
  }

  /**
   * Get event by ID
   */
  async getEvent(eventId: string): Promise<any> {
    if (this.isMockMode) {
      return this.getMockEvent(eventId);
    }

    try {
      const response = await this.calendar.events.get({
        calendarId: 'primary',
        eventId,
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to get calendar event', { eventId, error: error.message });
      throw new ServiceUnavailableError('Failed to fetch calendar event');
    }
  }

  /**
   * Create calendar event
   */
  async createEvent(event: any): Promise<any> {
    if (this.isMockMode) {
      return this.getMockCreatedEvent(event);
    }

    try {
      const response = await this.calendar.events.insert({
        calendarId: 'primary',
        requestBody: event,
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to create calendar event', { error: error.message });
      throw new ServiceUnavailableError('Failed to create calendar event');
    }
  }

  /**
   * Update calendar event
   */
  async updateEvent(eventId: string, event: any): Promise<any> {
    if (this.isMockMode) {
      return this.getMockUpdatedEvent(eventId, event);
    }

    try {
      const response = await this.calendar.events.patch({
        calendarId: 'primary',
        eventId,
        requestBody: event,
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to update calendar event', { eventId, error: error.message });
      throw new ServiceUnavailableError('Failed to update calendar event');
    }
  }

  /**
   * Delete calendar event
   */
  async deleteEvent(eventId: string): Promise<void> {
    if (this.isMockMode) {
      logger.info('Mock: Deleted calendar event', { eventId });
      return;
    }

    try {
      await this.calendar.events.delete({
        calendarId: 'primary',
        eventId,
      });
    } catch (error: any) {
      logger.error('Failed to delete calendar event', { eventId, error: error.message });
      throw new ServiceUnavailableError('Failed to delete calendar event');
    }
  }

  /**
   * Get meeting prep info (mock data with AI-generated insights)
   */
  async getMeetingPrep(eventId: string): Promise<any> {
    const event = await this.getEvent(eventId);

    if (this.isMockMode) {
      return {
        event,
        preparation: {
          agenda: ['Review Q3 results', 'Discuss Q4 strategy', 'Team updates'],
          participants: ['alice@example.com', 'bob@example.com'],
          context: 'This is a quarterly review meeting',
          suggestions: ['Prepare Q3 metrics', 'Review competitor analysis'],
        },
        mockMode: true,
      };
    }

    // In production, this would fetch context from other services
    // (CRM, Slack, Gmail) and use AI to generate prep materials
    return {
      event,
      preparation: {
        // Real preparation logic would go here
      },
    };
  }

  // ========== MOCK DATA METHODS ==========

  private getMockEvents(maxResults: number): any[] {
    const events = [];
    const now = Date.now();

    for (let i = 0; i < Math.min(maxResults, 5); i++) {
      const startTime = new Date(now + (i + 1) * 3600000); // i+1 hours from now
      const endTime = new Date(startTime.getTime() + 3600000); // 1 hour duration

      events.push({
        id: `event-${i + 1}`,
        summary: `Mock Event ${i + 1}`,
        description: `This is a mock calendar event for testing`,
        start: {
          dateTime: startTime.toISOString(),
          timeZone: 'America/Los_Angeles',
        },
        end: {
          dateTime: endTime.toISOString(),
          timeZone: 'America/Los_Angeles',
        },
        attendees: [
          { email: 'attendee1@example.com', responseStatus: 'accepted' },
          { email: 'attendee2@example.com', responseStatus: 'tentative' },
        ],
        location: 'Conference Room A',
        status: 'confirmed',
      });
    }

    return events;
  }

  private getMockEvent(eventId: string): any {
    const startTime = new Date(Date.now() + 3600000);
    const endTime = new Date(startTime.getTime() + 3600000);

    return {
      id: eventId,
      summary: `Mock Event ${eventId}`,
      description: 'This is a mock calendar event',
      start: {
        dateTime: startTime.toISOString(),
        timeZone: 'America/Los_Angeles',
      },
      end: {
        dateTime: endTime.toISOString(),
        timeZone: 'America/Los_Angeles',
      },
      attendees: [
        { email: 'attendee1@example.com', responseStatus: 'accepted' },
        { email: 'attendee2@example.com', responseStatus: 'tentative' },
      ],
      location: 'Conference Room A',
      status: 'confirmed',
    };
  }

  private getMockCreatedEvent(event: any): any {
    return {
      id: `event-${Date.now()}`,
      ...event,
      status: 'confirmed',
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };
  }

  private getMockUpdatedEvent(eventId: string, event: any): any {
    return {
      id: eventId,
      ...event,
      status: 'confirmed',
      updated: new Date().toISOString(),
    };
  }
}

// Singleton instance
export const calendarService = new CalendarService();
