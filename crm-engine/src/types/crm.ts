/**
 * CRM Data Models
 * Core types for contacts, companies, interactions, and relationships
 */

export enum ContactType {
  PERSON = 'person',
  COMPANY = 'company',
}

export enum InteractionType {
  EMAIL = 'email',
  SLACK_MESSAGE = 'slack_message',
  SLACK_MENTION = 'slack_mention',
  MEETING = 'meeting',
  PHONE_CALL = 'phone_call',
  NOTE = 'note',
}

export enum InteractionDirection {
  INBOUND = 'inbound',
  OUTBOUND = 'outbound',
  INTERNAL = 'internal',
}

export enum ContactStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ARCHIVED = 'archived',
}

export enum RelationshipType {
  CUSTOMER = 'customer',
  PROSPECT = 'prospect',
  PARTNER = 'partner',
  VENDOR = 'vendor',
  INVESTOR = 'investor',
  OTHER = 'other',
}

/**
 * Contact - Person or Company
 */
export interface Contact {
  id: string;
  tenantId: string;
  type: ContactType;

  // Basic info
  name: string;
  email?: string;
  phone?: string;
  avatar?: string;

  // Company-specific
  companyId?: string;  // If type=person, link to company
  companyName?: string;
  jobTitle?: string;
  department?: string;

  // Company details (if type=company)
  website?: string;
  industry?: string;
  size?: string;
  description?: string;

  // Social/Communication
  slackUserId?: string;
  slackUsername?: string;
  linkedinUrl?: string;
  twitterHandle?: string;

  // Relationship
  relationshipType: RelationshipType;
  status: ContactStatus;
  tags: string[];

  // Metadata
  source: string;  // slack, gmail, manual, etc.
  firstSeen: string;  // ISO timestamp
  lastSeen: string;  // ISO timestamp
  lastInteraction?: string;  // ISO timestamp

  // Computed/Analytics
  interactionCount: number;
  emailCount: number;
  slackMessageCount: number;
  meetingCount: number;

  // Ownership
  ownerId?: string;  // User who owns this contact
  ownerEmail?: string;

  // Timestamps
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
}

/**
 * Interaction - Any communication or activity with a contact
 */
export interface Interaction {
  id: string;
  tenantId: string;
  contactId: string;

  // Interaction details
  type: InteractionType;
  direction: InteractionDirection;
  subject?: string;
  content?: string;
  summary?: string;  // AI-generated summary

  // References
  externalId?: string;  // Slack message TS, Gmail message ID, etc.
  sourceService?: string;  // slack, gmail, calendar, etc.
  sourceUrl?: string;  // Deep link to original

  // Participants
  fromUserId?: string;
  fromEmail?: string;
  fromName?: string;
  toUserIds?: string[];
  toEmails?: string[];
  ccEmails?: string[];

  // Context
  channelId?: string;  // Slack channel
  channelName?: string;
  threadId?: string;  // Email thread or Slack thread

  // Sentiment & Intelligence
  sentiment?: 'positive' | 'neutral' | 'negative';
  importance?: 'high' | 'medium' | 'low';
  actionItems?: string[];
  mentions?: string[];  // @mentions or references

  // Timestamps
  timestamp: string;  // When the interaction happened
  createdAt: string;
  updatedAt: string;
}

/**
 * Note - User-created note about a contact
 */
export interface Note {
  id: string;
  tenantId: string;
  contactId: string;

  content: string;
  tags: string[];
  isPinned: boolean;

  // Authorship
  authorId: string;
  authorEmail: string;
  authorName: string;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Task - Follow-up or action item related to contact
 */
export interface Task {
  id: string;
  tenantId: string;
  contactId: string;

  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'high' | 'medium' | 'low';

  dueDate?: string;
  completedAt?: string;

  // Assignment
  assignedToId?: string;
  assignedToEmail?: string;

  // Authorship
  createdBy: string;
  createdByEmail: string;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Contact creation/update DTOs
 */
export interface CreateContactDTO {
  type: ContactType;
  name: string;
  email?: string;
  phone?: string;
  companyId?: string;
  companyName?: string;
  jobTitle?: string;
  website?: string;
  industry?: string;
  relationshipType: RelationshipType;
  tags?: string[];
  source?: string;
}

export interface UpdateContactDTO {
  name?: string;
  email?: string;
  phone?: string;
  jobTitle?: string;
  department?: string;
  website?: string;
  industry?: string;
  size?: string;
  description?: string;
  relationshipType?: RelationshipType;
  status?: ContactStatus;
  tags?: string[];
  ownerId?: string;
  ownerEmail?: string;
}

export interface CreateInteractionDTO {
  contactId: string;
  type: InteractionType;
  direction: InteractionDirection;
  subject?: string;
  content?: string;
  externalId?: string;
  sourceService?: string;
  fromEmail?: string;
  toEmails?: string[];
  timestamp?: string;
}

export interface ContactSearchQuery {
  query?: string;
  type?: ContactType;
  relationshipType?: RelationshipType;
  status?: ContactStatus;
  tags?: string[];
  ownerId?: string;
  limit?: number;
  offset?: number;
}
