export interface Config {
    port: number;
    nodeEnv: string;
    serviceName: string;
    gcpProjectId: string;
    gcpRegion: string;
    gmail: {
        clientId?: string;
        clientSecret?: string;
        redirectUri: string;
    };
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
        gmailEventsTopic: string;
    };
}
export declare const appConfig: Config;
//# sourceMappingURL=config.d.ts.map