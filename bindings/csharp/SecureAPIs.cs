using System.Runtime.InteropServices;
using System.Text.Json;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Options;

namespace SecureAPIs;

/// <summary>
/// Configuration for SecureAPIs security checks
/// </summary>
public class SecureAPIsConfig
{
    /// <summary>
    /// Rate limiting: requests per time window
    /// </summary>
    public int RateLimitRequests { get; set; } = 100;

    /// <summary>
    /// Rate limiting: time window in seconds
    /// </summary>
    public int RateLimitWindowSeconds { get; set; } = 60;

    /// <summary>
    /// JWT secret for token validation
    /// </summary>
    public string? JwtSecret { get; set; }

    /// <summary>
    /// Enable input validation and sanitization
    /// </summary>
    public bool EnableInputValidation { get; set; } = true;

    /// <summary>
    /// Enable CORS enforcement
    /// </summary>
    public bool EnableCors { get; set; } = false;

    /// <summary>
    /// Enable security headers injection
    /// </summary>
    public bool EnableSecurityHeaders { get; set; } = true;
}

/// <summary>
/// Internal result structure for P/Invoke marshaling
/// </summary>
[StructLayout(LayoutKind.Sequential)]
internal struct SecurityCheckResultInternal
{
    public int Allowed;
    public int StatusCode;
    public IntPtr ErrorMessage;
    public IntPtr HeadersJson;
}

/// <summary>
/// Main SecureAPIs class with P/Invoke bindings to Rust
/// </summary>
public class SecureAPIs : IDisposable
{
    private IntPtr _securityLayer;
    private bool _disposed = false;

    // P/Invoke declarations
    [DllImport("secureapis", CallingConvention = CallingConvention.Cdecl)]
    private static extern IntPtr secureapis_create_config(IntPtr configJson);

    [DllImport("secureapis", CallingConvention = CallingConvention.Cdecl)]
    private static extern IntPtr secureapis_check_request(
        IntPtr securityLayer,
        IntPtr method,
        IntPtr url,
        IntPtr headersJson,
        IntPtr body,
        IntPtr ip);

    [DllImport("secureapis", CallingConvention = CallingConvention.Cdecl)]
    private static extern void secureapis_free_security_layer(IntPtr securityLayer);

    [DllImport("secureapis", CallingConvention = CallingConvention.Cdecl)]
    private static extern void secureapis_free_result(IntPtr result);

    [DllImport("secureapis", CallingConvention = CallingConvention.Cdecl)]
    private static extern void secureapis_free_string(IntPtr str);

    /// <summary>
    /// Create a new SecureAPIs instance with configuration
    /// </summary>
    public SecureAPIs(SecureAPIsConfig config)
    {
        var configJson = JsonSerializer.Serialize(config);
        var configJsonPtr = Marshal.StringToHGlobalAnsi(configJson);

        try
        {
            _securityLayer = secureapis_create_config(configJsonPtr);
            if (_securityLayer == IntPtr.Zero)
            {
                throw new InvalidOperationException("Failed to create SecureAPIs security layer");
            }
        }
        finally
        {
            Marshal.FreeHGlobal(configJsonPtr);
        }
    }

    /// <summary>
    /// Check if a request is allowed by security rules
    /// </summary>
    public SecurityCheckResult CheckRequest(HttpRequest request)
    {
        // Extract request data
        var method = request.Method;
        var url = request.Path + request.QueryString;
        var ip = request.HttpContext.Connection.RemoteIpAddress?.ToString() ?? "127.0.0.1";

        // Extract headers as JSON
        var headers = new Dictionary<string, string>();
        foreach (var header in request.Headers)
        {
            headers[header.Key] = header.Value.ToString();
        }
        var headersJson = JsonSerializer.Serialize(headers);

        // Read body if present
        string body = "";
        if (request.ContentLength > 0 && request.Body != null)
        {
            using var reader = new StreamReader(request.Body);
            body = reader.ReadToEnd();
        }

        // Convert to pointers
        var methodPtr = Marshal.StringToHGlobalAnsi(method);
        var urlPtr = Marshal.StringToHGlobalAnsi(url);
        var headersJsonPtr = Marshal.StringToHGlobalAnsi(headersJson);
        var bodyPtr = Marshal.StringToHGlobalAnsi(body);
        var ipPtr = Marshal.StringToHGlobalAnsi(ip);

        IntPtr resultPtr = IntPtr.Zero;

        try
        {
            resultPtr = secureapis_check_request(
                _securityLayer,
                methodPtr,
                urlPtr,
                headersJsonPtr,
                bodyPtr,
                ipPtr);

            if (resultPtr == IntPtr.Zero)
            {
                throw new InvalidOperationException("Security check failed");
            }

            var result = Marshal.PtrToStructure<SecurityCheckResultInternal>(resultPtr);

            return new SecurityCheckResult
            {
                Allowed = result.Allowed == 1,
                StatusCode = result.StatusCode,
                ErrorMessage = result.ErrorMessage != IntPtr.Zero
                    ? Marshal.PtrToStringAnsi(result.ErrorMessage)
                    : null,
                HeadersJson = result.HeadersJson != IntPtr.Zero
                    ? Marshal.PtrToStringAnsi(result.HeadersJson)
                    : null
            };
        }
        finally
        {
            // Free allocated strings
            Marshal.FreeHGlobal(methodPtr);
            Marshal.FreeHGlobal(urlPtr);
            Marshal.FreeHGlobal(headersJsonPtr);
            Marshal.FreeHGlobal(bodyPtr);
            Marshal.FreeHGlobal(ipPtr);

            // Free result if allocated
            if (resultPtr != IntPtr.Zero)
            {
                secureapis_free_result(resultPtr);
            }
        }
    }

    /// <summary>
    /// Dispose of the SecureAPIs instance
    /// </summary>
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (_securityLayer != IntPtr.Zero)
            {
                secureapis_free_security_layer(_securityLayer);
                _securityLayer = IntPtr.Zero;
            }
            _disposed = true;
        }
    }

    ~SecureAPIs()
    {
        Dispose(false);
    }
}

/// <summary>
/// Result of a security check operation
/// </summary>
public class SecurityCheckResult
{
    /// <summary>
    /// Whether the request is allowed
    /// </summary>
    public bool Allowed { get; set; }

    /// <summary>
    /// HTTP status code to return if blocked
    /// </summary>
    public int StatusCode { get; set; }

    /// <summary>
    /// Error message if request is blocked
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Additional headers to add (JSON)
    /// </summary>
    public string? HeadersJson { get; set; }
}