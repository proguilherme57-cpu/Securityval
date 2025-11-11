const { SecureAPIs: SecureAPIsNative } = require('./build/Release/secureapis.node');

class SecureAPIs {
    constructor(config = {}) {
        this.native = new SecureAPIsNative(config);
    }

    checkRequest(request) {
        return this.native.checkRequest(request);
    }

    getVersion() {
        return this.native.getVersion();
    }
}

// Express.js middleware
function SecureAPIsMiddleware(config = {}) {
    const secureAPIs = new SecureAPIs(config);

    return (req, res, next) => {
        // Build request object
        const request = {
            method: req.method,
            url: req.url,
            headers: req.headers,
            body: req.body ? JSON.stringify(req.body) : '',
            ip: req.ip || req.connection.remoteAddress
        };

        // Check request
        const result = secureAPIs.checkRequest(request);

        if (!result.allowed) {
            // Block request
            const statusCode = getStatusCode(result.reason);
            return res.status(statusCode).json({
                error: result.reason,
                statusCode: statusCode
            });
        }

        // Add security headers if enabled
        if (config.enableSecurityHeaders !== false) {
            res.setHeader('X-Content-Type-Options', 'nosniff');
            res.setHeader('X-Frame-Options', 'DENY');
            res.setHeader('X-XSS-Protection', '1; mode=block');
            res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
            res.setHeader('Content-Security-Policy', "default-src 'self'");
        }

        next();
    };
}

function getStatusCode(reason) {
    if (reason.includes('Rate limit')) return 429;
    if (reason.includes('Invalid input') || reason.includes('SQL') || reason.includes('XSS')) return 400;
    if (reason.includes('JWT') || reason.includes('token')) return 401;
    if (reason.includes('threat') || reason.includes('attack')) return 403;
    return 400;
}

module.exports = {
    SecureAPIs,
    SecureAPIsMiddleware
};