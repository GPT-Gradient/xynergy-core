import winston from 'winston';
/**
 * Structured logger using Winston
 * Formats logs as JSON for Cloud Logging compatibility
 */
export declare const logger: winston.Logger;
/**
 * Log HTTP request
 */
export declare const logRequest: (req: any, duration?: number) => void;
/**
 * Log HTTP response
 */
export declare const logResponse: (req: any, res: any, duration: number) => void;
//# sourceMappingURL=logger.d.ts.map