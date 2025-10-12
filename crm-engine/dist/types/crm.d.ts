/**
 * CRM Data Models
 * Core types for contacts, companies, interactions, and relationships
 */
export declare enum ContactType {
    PERSON = "person",
    COMPANY = "company"
}
export declare enum InteractionType {
    EMAIL = "email",
    SLACK_MESSAGE = "slack_message",
    SLACK_MENTION = "slack_mention",
    MEETING = "meeting",
    PHONE_CALL = "phone_call",
    NOTE = "note"
}
export declare enum InteractionDirection {
    INBOUND = "inbound",
    OUTBOUND = "outbound",
    INTERNAL = "internal"
}
export declare enum ContactStatus {
    ACTIVE = "active",
    INACTIVE = "inactive",
    ARCHIVED = "archived"
}
export declare enum RelationshipType {
    CUSTOMER = "customer",
    PROSPECT = "prospect",
    PARTNER = "partner",
    VENDOR = "vendor",
    INVESTOR = "investor",
    OTHER = "other"
}
/**
 * Contact - Person or Company
 */
export interface Contact {
    id: string;
    tenantId: string;
    type: ContactType;
    name: string;
    email?: string;
    phone?: string;
    avatar?: string;
    companyId?: string;
    companyName?: string;
    jobTitle?: string;
    department?: string;
    website?: string;
    industry?: string;
    size?: string;
    description?: string;
    slackUserId?: string;
    slackUsername?: string;
    linkedinUrl?: string;
    twitterHandle?: string;
    relationshipType: RelationshipType;
    status: ContactStatus;
    tags: string[];
    source: string;
    firstSeen: string;
    lastSeen: string;
    lastInteraction?: string;
    interactionCount: number;
    emailCount: number;
    slackMessageCount: number;
    meetingCount: number;
    ownerId?: string;
    ownerEmail?: string;
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
    type: InteractionType;
    direction: InteractionDirection;
    subject?: string;
    content?: string;
    summary?: string;
    externalId?: string;
    sourceService?: string;
    sourceUrl?: string;
    fromUserId?: string;
    fromEmail?: string;
    fromName?: string;
    toUserIds?: string[];
    toEmails?: string[];
    ccEmails?: string[];
    channelId?: string;
    channelName?: string;
    threadId?: string;
    sentiment?: 'positive' | 'neutral' | 'negative';
    importance?: 'high' | 'medium' | 'low';
    actionItems?: string[];
    mentions?: string[];
    timestamp: string;
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
    authorId: string;
    authorEmail: string;
    authorName: string;
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
    assignedToId?: string;
    assignedToEmail?: string;
    createdBy: string;
    createdByEmail: string;
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
    cursor?: string;
}
//# sourceMappingURL=crm.d.ts.map