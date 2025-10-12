"use strict";
/**
 * CRM Data Models
 * Core types for contacts, companies, interactions, and relationships
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RelationshipType = exports.ContactStatus = exports.InteractionDirection = exports.InteractionType = exports.ContactType = void 0;
var ContactType;
(function (ContactType) {
    ContactType["PERSON"] = "person";
    ContactType["COMPANY"] = "company";
})(ContactType || (exports.ContactType = ContactType = {}));
var InteractionType;
(function (InteractionType) {
    InteractionType["EMAIL"] = "email";
    InteractionType["SLACK_MESSAGE"] = "slack_message";
    InteractionType["SLACK_MENTION"] = "slack_mention";
    InteractionType["MEETING"] = "meeting";
    InteractionType["PHONE_CALL"] = "phone_call";
    InteractionType["NOTE"] = "note";
})(InteractionType || (exports.InteractionType = InteractionType = {}));
var InteractionDirection;
(function (InteractionDirection) {
    InteractionDirection["INBOUND"] = "inbound";
    InteractionDirection["OUTBOUND"] = "outbound";
    InteractionDirection["INTERNAL"] = "internal";
})(InteractionDirection || (exports.InteractionDirection = InteractionDirection = {}));
var ContactStatus;
(function (ContactStatus) {
    ContactStatus["ACTIVE"] = "active";
    ContactStatus["INACTIVE"] = "inactive";
    ContactStatus["ARCHIVED"] = "archived";
})(ContactStatus || (exports.ContactStatus = ContactStatus = {}));
var RelationshipType;
(function (RelationshipType) {
    RelationshipType["CUSTOMER"] = "customer";
    RelationshipType["PROSPECT"] = "prospect";
    RelationshipType["PARTNER"] = "partner";
    RelationshipType["VENDOR"] = "vendor";
    RelationshipType["INVESTOR"] = "investor";
    RelationshipType["OTHER"] = "other";
})(RelationshipType || (exports.RelationshipType = RelationshipType = {}));
//# sourceMappingURL=crm.js.map