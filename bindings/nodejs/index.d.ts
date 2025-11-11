export interface SecureAPIsConfig {
    rateLimitRequests?: number;
    rateLimitWindowSeconds?: number;
    jwtSecret?: string;
    enableInputValidation?: boolean;
    enableSecurityHeaders?: boolean;
    enableCors?: boolean;
}

export interface RequestCheck {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: string;
    ip: string;
}

export interface CheckResult {
    allowed: boolean;
    reason: string;
}

export class SecureAPIs {
    constructor(config?: SecureAPIsConfig);
    checkRequest(request: RequestCheck): CheckResult;
    getVersion(): string;
}

export function SecureAPIsMiddleware(config?: SecureAPIsConfig): any;