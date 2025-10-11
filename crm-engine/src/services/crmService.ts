import { getFirestore } from '../config/firebase';
import { logger } from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';
import {
  Contact,
  Interaction,
  Note,
  ContactType,
  ContactStatus,
  RelationshipType,
  CreateContactDTO,
  UpdateContactDTO,
  CreateInteractionDTO,
  ContactSearchQuery,
} from '../types/crm';
import { NotFoundError, ValidationError } from '../middleware/errorHandler';

/**
 * CRM Service - Core contact and interaction management
 */
export class CRMService {
  private get db() {
    return getFirestore();
  }

  /**
   * Create a new contact
   */
  async createContact(tenantId: string, userId: string, userEmail: string, data: CreateContactDTO): Promise<Contact> {
    const contactId = uuidv4();
    const now = new Date().toISOString();

    const contact: Contact = {
      id: contactId,
      tenantId,
      type: data.type,
      name: data.name,
      email: data.email,
      phone: data.phone,
      companyId: data.companyId,
      companyName: data.companyName,
      jobTitle: data.jobTitle,
      website: data.website,
      industry: data.industry,
      relationshipType: data.relationshipType || RelationshipType.PROSPECT,
      status: ContactStatus.ACTIVE,
      tags: data.tags || [],
      source: data.source || 'manual',
      firstSeen: now,
      lastSeen: now,
      interactionCount: 0,
      emailCount: 0,
      slackMessageCount: 0,
      meetingCount: 0,
      ownerId: userId,
      ownerEmail: userEmail,
      createdAt: now,
      updatedAt: now,
      createdBy: userId,
      updatedBy: userId,
    };

    await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts')
      .doc(contactId)
      .set(contact);

    logger.info('Contact created', { contactId, name: contact.name, type: contact.type });

    return contact;
  }

  /**
   * Get contact by ID
   */
  async getContact(tenantId: string, contactId: string): Promise<Contact> {
    const doc = await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts')
      .doc(contactId)
      .get();

    if (!doc.exists) {
      throw new NotFoundError(`Contact ${contactId} not found`);
    }

    return doc.data() as Contact;
  }

  /**
   * Update contact
   */
  async updateContact(
    tenantId: string,
    contactId: string,
    userId: string,
    data: UpdateContactDTO
  ): Promise<Contact> {
    const contact = await this.getContact(tenantId, contactId);

    const updated: Partial<Contact> = {
      ...data,
      updatedAt: new Date().toISOString(),
      updatedBy: userId,
    };

    await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts')
      .doc(contactId)
      .update(updated);

    logger.info('Contact updated', { contactId, updates: Object.keys(data) });

    return { ...contact, ...updated } as Contact;
  }

  /**
   * Delete contact (soft delete - set to archived)
   */
  async deleteContact(tenantId: string, contactId: string, userId: string): Promise<void> {
    await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts')
      .doc(contactId)
      .update({
        status: ContactStatus.ARCHIVED,
        updatedAt: new Date().toISOString(),
        updatedBy: userId,
      });

    logger.info('Contact archived', { contactId });
  }

  /**
   * Search/list contacts with filtering (cursor-based pagination for efficiency)
   */
  async searchContacts(
    tenantId: string,
    query: ContactSearchQuery
  ): Promise<{ contacts: Contact[]; total: number; hasMore: boolean; nextCursor?: string }> {
    let ref: any = this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts');

    // Apply filters
    if (query.type) {
      ref = ref.where('type', '==', query.type);
    }

    if (query.relationshipType) {
      ref = ref.where('relationshipType', '==', query.relationshipType);
    }

    if (query.status) {
      ref = ref.where('status', '==', query.status);
    } else {
      // Default: only show active contacts
      ref = ref.where('status', '==', ContactStatus.ACTIVE);
    }

    if (query.ownerId) {
      ref = ref.where('ownerId', '==', query.ownerId);
    }

    // Apply limit (max 100 per page to prevent large queries)
    const limit = Math.min(query.limit || 50, 100);

    // Cursor-based pagination for better performance
    if (query.cursor) {
      try {
        const lastDocSnap = await this.db
          .collection('tenants')
          .doc(tenantId)
          .collection('contacts')
          .doc(query.cursor)
          .get();

        if (lastDocSnap.exists) {
          ref = ref.startAfter(lastDocSnap);
        }
      } catch (error: any) {
        logger.warn('Invalid pagination cursor', { cursor: query.cursor, error: error.message });
        // Continue without cursor if invalid
      }
    }

    // Fetch one extra to determine if there are more results
    ref = ref.limit(limit + 1);

    const snapshot = await ref.get();
    const contacts: Contact[] = [];

    snapshot.forEach((doc: any) => {
      contacts.push({ id: doc.id, ...doc.data() } as Contact);
    });

    // Check if there are more results
    const hasMore = contacts.length > limit;
    const resultContacts = hasMore ? contacts.slice(0, limit) : contacts;

    // Text search on name/email (client-side filtering for now)
    let filteredContacts = resultContacts;
    if (query.query) {
      const searchLower = query.query.toLowerCase();
      filteredContacts = resultContacts.filter(
        (c) =>
          c.name.toLowerCase().includes(searchLower) ||
          c.email?.toLowerCase().includes(searchLower) ||
          c.companyName?.toLowerCase().includes(searchLower)
      );
    }

    return {
      contacts: filteredContacts,
      total: filteredContacts.length,
      hasMore,
      nextCursor: hasMore && filteredContacts.length > 0
        ? filteredContacts[filteredContacts.length - 1].id
        : undefined,
    };
  }

  /**
   * Find or create contact by email
   */
  async findOrCreateContactByEmail(
    tenantId: string,
    userId: string,
    userEmail: string,
    email: string,
    name: string,
    source: string
  ): Promise<Contact> {
    // Try to find existing contact
    const snapshot = await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts')
      .where('email', '==', email)
      .limit(1)
      .get();

    if (!snapshot.empty) {
      const existingContact = snapshot.docs[0].data() as Contact;

      // Update lastSeen
      await this.db
        .collection('tenants')
        .doc(tenantId)
        .collection('contacts')
        .doc(existingContact.id)
        .update({
          lastSeen: new Date().toISOString(),
        });

      return existingContact;
    }

    // Create new contact
    return this.createContact(tenantId, userId, userEmail, {
      type: ContactType.PERSON,
      name,
      email,
      relationshipType: RelationshipType.PROSPECT,
      source,
    });
  }

  /**
   * Create interaction
   */
  async createInteraction(tenantId: string, data: CreateInteractionDTO): Promise<Interaction> {
    const interactionId = uuidv4();
    const now = new Date().toISOString();

    const interaction: Interaction = {
      id: interactionId,
      tenantId,
      contactId: data.contactId,
      type: data.type,
      direction: data.direction,
      subject: data.subject,
      content: data.content,
      externalId: data.externalId,
      sourceService: data.sourceService,
      fromEmail: data.fromEmail,
      toEmails: data.toEmails,
      timestamp: data.timestamp || now,
      createdAt: now,
      updatedAt: now,
    };

    // Save interaction
    await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('interactions')
      .doc(interactionId)
      .set(interaction);

    // Update contact interaction counts
    await this.incrementContactInteractions(tenantId, data.contactId, data.type);

    logger.info('Interaction created', { interactionId, contactId: data.contactId, type: data.type });

    return interaction;
  }

  /**
   * Get interactions for a contact
   */
  async getContactInteractions(
    tenantId: string,
    contactId: string,
    limit: number = 50
  ): Promise<Interaction[]> {
    const snapshot = await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('interactions')
      .where('contactId', '==', contactId)
      .orderBy('timestamp', 'desc')
      .limit(limit)
      .get();

    const interactions: Interaction[] = [];
    snapshot.forEach((doc: any) => {
      interactions.push(doc.data() as Interaction);
    });

    return interactions;
  }

  /**
   * Increment contact interaction counts
   */
  private async incrementContactInteractions(tenantId: string, contactId: string, interactionType: string): Promise<void> {
    const contact = await this.getContact(tenantId, contactId);

    const updates: any = {
      interactionCount: (contact.interactionCount || 0) + 1,
      lastInteraction: new Date().toISOString(),
      lastSeen: new Date().toISOString(),
    };

    // Update specific counts
    if (interactionType === 'email') {
      updates.emailCount = (contact.emailCount || 0) + 1;
    } else if (interactionType.startsWith('slack')) {
      updates.slackMessageCount = (contact.slackMessageCount || 0) + 1;
    } else if (interactionType === 'meeting') {
      updates.meetingCount = (contact.meetingCount || 0) + 1;
    }

    await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts')
      .doc(contactId)
      .update(updates);
  }

  /**
   * Create note for contact
   */
  async createNote(tenantId: string, contactId: string, userId: string, userEmail: string, userName: string, content: string, tags: string[] = []): Promise<Note> {
    const noteId = uuidv4();
    const now = new Date().toISOString();

    const note: Note = {
      id: noteId,
      tenantId,
      contactId,
      content,
      tags,
      isPinned: false,
      authorId: userId,
      authorEmail: userEmail,
      authorName: userName,
      createdAt: now,
      updatedAt: now,
    };

    await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('notes')
      .doc(noteId)
      .set(note);

    logger.info('Note created', { noteId, contactId });

    return note;
  }

  /**
   * Get notes for contact
   */
  async getContactNotes(tenantId: string, contactId: string): Promise<Note[]> {
    const snapshot = await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('notes')
      .where('contactId', '==', contactId)
      .orderBy('createdAt', 'desc')
      .get();

    const notes: Note[] = [];
    snapshot.forEach((doc: any) => {
      notes.push(doc.data() as Note);
    });

    return notes;
  }

  /**
   * Get CRM statistics
   */
  async getStatistics(tenantId: string): Promise<any> {
    const contactsSnapshot = await this.db
      .collection('tenants')
      .doc(tenantId)
      .collection('contacts')
      .where('status', '==', ContactStatus.ACTIVE)
      .get();

    const stats = {
      totalContacts: contactsSnapshot.size,
      people: 0,
      companies: 0,
      byRelationshipType: {} as any,
      bySource: {} as any,
    };

    contactsSnapshot.forEach((doc: any) => {
      const contact = doc.data() as Contact;

      if (contact.type === ContactType.PERSON) {
        stats.people++;
      } else {
        stats.companies++;
      }

      stats.byRelationshipType[contact.relationshipType] =
        (stats.byRelationshipType[contact.relationshipType] || 0) + 1;

      stats.bySource[contact.source] =
        (stats.bySource[contact.source] || 0) + 1;
    });

    return stats;
  }
}

export const crmService = new CRMService();
