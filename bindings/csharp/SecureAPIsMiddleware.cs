using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Options;
using System.Threading.Tasks;

namespace SecureAPIs;

/// <summary>
/// ASP.NET Core middleware for SecureAPIs security checks
/// </summary>
public class SecureAPIsMiddleware
{
    private readonly RequestDelegate _next;
    private readonly SecureAPIs _secureAPIs;

    public SecureAPIsMiddleware(RequestDelegate next, IOptions<SecureAPIsConfig> config)
    {
        _next = next;
        _secureAPIs = new SecureAPIs(config.Value);
    }

    /// <summary>
    /// Process the HTTP request through security checks
    /// </summary>
    public async Task InvokeAsync(HttpContext context)
    {
        // Run security check
        var result = _secureAPIs.CheckRequest(context.Request);

        if (!result.Allowed)
        {
            // Request blocked - return error response
            context.Response.StatusCode = result.StatusCode;
            context.Response.ContentType = "application/json";

            var errorResponse = new
            {
                error = result.ErrorMessage ?? "Request blocked by security policy",
                statusCode = result.StatusCode
            };

            await context.Response.WriteAsJsonAsync(errorResponse);
            return;
        }

        // Request allowed - add security headers if provided
        if (!string.IsNullOrEmpty(result.HeadersJson))
        {
            try
            {
                var headers = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(result.HeadersJson);
                if (headers != null)
                {
                    foreach (var header in headers)
                    {
                        context.Response.Headers[header.Key] = header.Value;
                    }
                }
            }
            catch
            {
                // Ignore header parsing errors
            }
        }

        // Continue to next middleware
        await _next(context);
    }
}

/// <summary>
/// Extension methods for adding SecureAPIs middleware
/// </summary>
public static class SecureAPIsMiddlewareExtensions
{
    /// <summary>
    /// Add SecureAPIs middleware to the pipeline
    /// </summary>
    public static IApplicationBuilder UseSecureAPIs(
        this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<SecureAPIsMiddleware>();
    }

    /// <summary>
    /// Add SecureAPIs middleware with custom configuration
    /// </summary>
    public static IApplicationBuilder UseSecureAPIs(
        this IApplicationBuilder builder,
        Action<SecureAPIsConfig> configure)
    {
        var config = new SecureAPIsConfig();
        configure(config);

        builder.UseMiddleware<SecureAPIsMiddleware>(
            Options.Create(config));

        return builder;
    }
}