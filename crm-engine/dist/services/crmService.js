"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.crmService = exports.CRMService = void 0;
const firebase_1 = require("../config/firebase");
const logger_1 = require("../utils/logger");
const uuid_1 = require("uuid");
const crm_1 = require("../types/crm");
const errorHandler_1 = require("../middleware/errorHandler");
/**
 * CRM Service - Core contact and interaction management
 */
class CRMService {
    get db() {
        return (0, firebase_1.getFirestore)();
    }
    /**
     * Create a new contact
     */
    async createContact(tenantId, userId, userEmail, data) {
        const contactId = (0, uuid_1.v4)();
        const now = new Date().toISOString();
        const contact = {
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
            relationshipType: data.relationshipType || crm_1.RelationshipType.PROSPECT,
            status: crm_1.ContactStatus.ACTIVE,
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
        logger_1.logger.info('Contact created', { contactId, name: contact.name, type: contact.type });
        return contact;
    }
    /**
     * Get contact by ID
     */
    async getContact(tenantId, contactId) {
        const doc = await this.db
            .collection('tenants')
            .doc(tenantId)
            .collection('contacts')
            .doc(contactId)
            .get();
        if (!doc.exists) {
            throw new errorHandler_1.NotFoundError(`Contact ${contactId} not found`);
        }
        return doc.data();
    }
    /**
     * Update contact
     */
    async updateContact(tenantId, contactId, userId, data) {
        const contact = await this.getContact(tenantId, contactId);
        const updated = {
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
        logger_1.logger.info('Contact updated', { contactId, updates: Object.keys(data) });
        return { ...contact, ...updated };
    }
    /**
     * Delete contact (soft delete - set to archived)
     */
    async deleteContact(tenantId, contactId, userId) {
        await this.db
            .collection('tenants')
            .doc(tenantId)
            .collection('contacts')
            .doc(contactId)
            .update({
            status: crm_1.ContactStatus.ARCHIVED,
            updatedAt: new Date().toISOString(),
            updatedBy: userId,
        });
        logger_1.logger.info('Contact archived', { contactId });
    }
    /**
     * Search/list contacts with filtering (cursor-based pagination for efficiency)
     */
    async searchContacts(tenantId, query) {
        let ref = this.db
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
        }
        else {
            // Default: only show active contacts
            ref = ref.where('status', '==', crm_1.ContactStatus.ACTIVE);
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
            }
            catch (error) {
                logger_1.logger.warn('Invalid pagination cursor', { cursor: query.cursor, error: error.message });
                // Continue without cursor if invalid
            }
        }
        // Fetch one extra to determine if there are more results
        ref = ref.limit(limit + 1);
        const snapshot = await ref.get();
        const contacts = [];
        snapshot.forEach((doc) => {
            contacts.push({ id: doc.id, ...doc.data() });
        });
        // Check if there are more results
        const hasMore = contacts.length > limit;
        const resultContacts = hasMore ? contacts.slice(0, limit) : contacts;
        // Text search on name/email (client-side filtering for now)
        let filteredContacts = resultContacts;
        if (query.query) {
            const searchLower = query.query.toLowerCase();
            filteredContacts = resultContacts.filter((c) => c.name.toLowerCase().includes(searchLower) ||
                c.email?.toLowerCase().includes(searchLower) ||
                c.companyName?.toLowerCase().includes(searchLower));
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
    async findOrCreateContactByEmail(tenantId, userId, userEmail, email, name, source) {
        // Try to find existing contact
        const snapshot = await this.db
            .collection('tenants')
            .doc(tenantId)
            .collection('contacts')
            .where('email', '==', email)
            .limit(1)
            .get();
        if (!snapshot.empty) {
            const existingContact = snapshot.docs[0].data();
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
            type: crm_1.ContactType.PERSON,
            name,
            email,
            relationshipType: crm_1.RelationshipType.PROSPECT,
            source,
        });
    }
    /**
     * Create interaction
     */
    async createInteraction(tenantId, data) {
        const interactionId = (0, uuid_1.v4)();
        const now = new Date().toISOString();
        const interaction = {
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
        logger_1.logger.info('Interaction created', { interactionId, contactId: data.contactId, type: data.type });
        return interaction;
    }
    /**
     * Get interactions for a contact
     */
    async getContactInteractions(tenantId, contactId, limit = 50) {
        const snapshot = await this.db
            .collection('tenants')
            .doc(tenantId)
            .collection('interactions')
            .where('contactId', '==', contactId)
            .orderBy('timestamp', 'desc')
            .limit(limit)
            .get();
        const interactions = [];
        snapshot.forEach((doc) => {
            interactions.push(doc.data());
        });
        return interactions;
    }
    /**
     * Increment contact interaction counts
     */
    async incrementContactInteractions(tenantId, contactId, interactionType) {
        const contact = await this.getContact(tenantId, contactId);
        const updates = {
            interactionCount: (contact.interactionCount || 0) + 1,
            lastInteraction: new Date().toISOString(),
            lastSeen: new Date().toISOString(),
        };
        // Update specific counts
        if (interactionType === 'email') {
            updates.emailCount = (contact.emailCount || 0) + 1;
        }
        else if (interactionType.startsWith('slack')) {
            updates.slackMessageCount = (contact.slackMessageCount || 0) + 1;
        }
        else if (interactionType === 'meeting') {
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
    async createNote(tenantId, contactId, userId, userEmail, userName, content, tags = []) {
        const noteId = (0, uuid_1.v4)();
        const now = new Date().toISOString();
        const note = {
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
        logger_1.logger.info('Note created', { noteId, contactId });
        return note;
    }
    /**
     * Get notes for contact
     */
    async getContactNotes(tenantId, contactId) {
        const snapshot = await this.db
            .collection('tenants')
            .doc(tenantId)
            .collection('notes')
            .where('contactId', '==', contactId)
            .orderBy('createdAt', 'desc')
            .get();
        const notes = [];
        snapshot.forEach((doc) => {
            notes.push(doc.data());
        });
        return notes;
    }
    /**
     * Get CRM statistics
     */
    async getStatistics(tenantId) {
        const contactsSnapshot = await this.db
            .collection('tenants')
            .doc(tenantId)
            .collection('contacts')
            .where('status', '==', crm_1.ContactStatus.ACTIVE)
            .get();
        const stats = {
            totalContacts: contactsSnapshot.size,
            people: 0,
            companies: 0,
            byRelationshipType: {},
            bySource: {},
        };
        contactsSnapshot.forEach((doc) => {
            const contact = doc.data();
            if (contact.type === crm_1.ContactType.PERSON) {
                stats.people++;
            }
            else {
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
exports.CRMService = CRMService;
exports.crmService = new CRMService();
//# sourceMappingURL=crmService.js.map