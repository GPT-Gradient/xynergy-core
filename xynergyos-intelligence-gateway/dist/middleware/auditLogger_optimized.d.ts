/**
 * Audit Logging Middleware - OPTIMIZED VERSION
 * All security and performance issues fixed
 */
import { Request, Response, NextFunction } from 'express';
interface AuditEvent {
    log_id?: string;
    user_id: string;
    tenant_id?: string;
    action: string;
    resource: string;
    resource_id?: string;
    granted: boolean;
    reason?: string;
    metadata?: Record<string, any>;
    ip_address?: string;
    user_agent?: string;
    timestamp?: string;
    severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
    request_id?: string;
}
export declare function auditLogger(): (req: Request, res: Response, next: NextFunction) => Promise<void>;
export declare function securityAlert(action: string, severity?: AuditEvent['severity']): (req: Request, res: Response, next: NextFunction) => Promise<void>;
export declare function complianceTracker(complianceType: 'GDPR' | 'HIPAA' | 'SOC2' | 'PCI'): (req: Request, res: Response, next: NextFunction) => Promise<void>;
export default auditLogger;
//# sourceMappingURL=auditLogger_optimized.d.ts.map