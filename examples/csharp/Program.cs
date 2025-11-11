using SecureAPIs;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure JWT authentication (for demonstration)
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes("your-super-secret-jwt-key"))
        };
    });

// Configure SecureAPIs
builder.Services.Configure<SecureAPIsConfig>(config =>
{
    config.RateLimitRequests = 100;        // 100 requests per window
    config.RateLimitWindowSeconds = 60;    // 60 second window
    config.JwtSecret = "your-super-secret-jwt-key";  // Must match JWT signing key
    config.EnableInputValidation = true;   // SQL injection, XSS protection
    config.EnableSecurityHeaders = true;   // Security headers
    config.EnableCors = true;              // CORS support
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// Add SecureAPIs middleware FIRST (before other middleware)
app.UseSecureAPIs();

// Other middleware
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();