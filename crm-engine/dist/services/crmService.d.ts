import { Contact, Interaction, Note, CreateContactDTO, UpdateContactDTO, CreateInteractionDTO, ContactSearchQuery } from '../types/crm';
/**
 * CRM Service - Core contact and interaction management
 */
export declare class CRMService {
    private get db();
    /**
     * Create a new contact
     */
    createContact(tenantId: string, userId: string, userEmail: string, data: CreateContactDTO): Promise<Contact>;
    /**
     * Get contact by ID
     */
    getContact(tenantId: string, contactId: string): Promise<Contact>;
    /**
     * Update contact
     */
    updateContact(tenantId: string, contactId: string, userId: string, data: UpdateContactDTO): Promise<Contact>;
    /**
     * Delete contact (soft delete - set to archived)
     */
    deleteContact(tenantId: string, contactId: string, userId: string): Promise<void>;
    /**
     * Search/list contacts with filtering (cursor-based pagination for efficiency)
     */
    searchContacts(tenantId: string, query: ContactSearchQuery): Promise<{
        contacts: Contact[];
        total: number;
        hasMore: boolean;
        nextCursor?: string;
    }>;
    /**
     * Find or create contact by email
     */
    findOrCreateContactByEmail(tenantId: string, userId: string, userEmail: string, email: string, name: string, source: string): Promise<Contact>;
    /**
     * Create interaction
     */
    createInteraction(tenantId: string, data: CreateInteractionDTO): Promise<Interaction>;
    /**
     * Get interactions for a contact
     */
    getContactInteractions(tenantId: string, contactId: string, limit?: number): Promise<Interaction[]>;
    /**
     * Increment contact interaction counts
     */
    private incrementContactInteractions;
    /**
     * Create note for contact
     */
    createNote(tenantId: string, contactId: string, userId: string, userEmail: string, userName: string, content: string, tags?: string[]): Promise<Note>;
    /**
     * Get notes for contact
     */
    getContactNotes(tenantId: string, contactId: string): Promise<Note[]>;
    /**
     * Get CRM statistics
     */
    getStatistics(tenantId: string): Promise<any>;
}
export declare const crmService: CRMService;
//# sourceMappingURL=crmService.d.ts.map