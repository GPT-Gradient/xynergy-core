"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.logger = void 0;
const winston_1 = __importDefault(require("winston"));
const config_1 = require("../config/config");
const logFormat = winston_1.default.format.combine(winston_1.default.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }), winston_1.default.format.errors({ stack: true }), winston_1.default.format.splat(), winston_1.default.format.json());
const logger = winston_1.default.createLogger({
    level: config_1.appConfig.nodeEnv === 'production' ? 'info' : 'debug',
    format: logFormat,
    defaultMeta: {
        service: 'xynergyos-intelligence-gateway',
        environment: config_1.appConfig.nodeEnv,
    },
    transports: [
        new winston_1.default.transports.Console({
            format: config_1.appConfig.nodeEnv === 'production'
                ? winston_1.default.format.json()
                : winston_1.default.format.combine(winston_1.default.format.colorize(), winston_1.default.format.simple()),
        }),
    ],
});
exports.logger = logger;
//# sourceMappingURL=logger.js.map