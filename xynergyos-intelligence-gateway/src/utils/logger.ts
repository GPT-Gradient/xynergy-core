import winston from 'winston';
import { appConfig } from '../config/config';

const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

const logger = winston.createLogger({
  level: appConfig.nodeEnv === 'production' ? 'info' : 'debug',
  format: logFormat,
  defaultMeta: {
    service: 'xynergyos-intelligence-gateway',
    environment: appConfig.nodeEnv,
  },
  transports: [
    new winston.transports.Console({
      format: appConfig.nodeEnv === 'production'
        ? winston.format.json()
        : winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          ),
    }),
  ],
});

export { logger };
