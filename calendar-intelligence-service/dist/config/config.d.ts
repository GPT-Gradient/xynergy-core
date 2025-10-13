export interface Config {
    port: number;
    nodeEnv: string;
    serviceName: string;
    gcpProjectId: string;
    gcpRegion: string;
    firebase: {
        projectId: string;
        serviceAccountPath?: string;
    };
    redis: {
        host: string;
        port: number;
        password?: string;
    };
    rateLimit: {
        windowMs: number;
        maxRequests: number;
    };
    cors: {
        origins: string[];
    };
    pubsub: {
        crmEventsTopic: string;
    };
}
export declare const appConfig: Config;
//# sourceMappingURL=config.d.ts.map