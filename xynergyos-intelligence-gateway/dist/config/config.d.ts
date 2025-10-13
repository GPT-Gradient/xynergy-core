interface Config {
    port: number;
    nodeEnv: string;
    gcpProjectId: string;
    gcpRegion: string;
    services: {
        aiRouting: string;
        aiAssistant: string;
        slackIntelligence: string;
        gmailIntelligence: string;
        calendarIntelligence: string;
        crmEngine: string;
        marketingEngine: string;
        asoEngine: string;
        researchCoordinator: string;
        memoryService: string;
    };
    redis: {
        host: string;
        port: number;
        password?: string;
    };
    firebase: {
        projectId: string;
        serviceAccountPath?: string;
    };
    rateLimit: {
        windowMs: number;
        maxRequests: number;
    };
    cors: {
        origins: string[];
    };
}
export declare const appConfig: Config;
export {};
//# sourceMappingURL=config.d.ts.map