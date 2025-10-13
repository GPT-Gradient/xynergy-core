import winston from 'winston';
import { appConfig } from '../config/config';

const logLevel = appConfig.nodeEnv === 'production' ? 'info' : 'debug';

/**
 * Structured logger using Winston
 * Formats logs as JSON for Cloud Logging compatibility
 */
export const logger = winston.createLogger({
  level: logLevel,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: appConfig.serviceName,
    environment: appConfig.nodeEnv,
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ timestamp, level, message, ...meta }) => {
          const metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
          return `${timestamp} [${level}]: ${message} ${metaStr}`;
        })
      ),
    }),
  ],
});

/**
 * Log HTTP request
 */
export const logRequest = (req: any, duration?: number) => {
  logger.info('HTTP Request', {
    method: req.method,
    path: req.path,
    requestId: req.requestId,
    userId: req.user?.uid,
    duration: duration ? `${duration}ms` : undefined,
  });
};

/**
 * Log HTTP response
 */
export const logResponse = (req: any, res: any, duration: number) => {
  logger.info('HTTP Response', {
    method: req.method,
    path: req.path,
    requestId: req.requestId,
    statusCode: res.statusCode,
    duration: `${duration}ms`,
  });
};
