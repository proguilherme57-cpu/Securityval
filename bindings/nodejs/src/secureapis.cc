#include <napi.h>
#include <string>
#include <cstring>
#include <memory>

// External C functions from Rust FFI
extern "C" {
    void* secureapis_create_config(const char* json_config);
    void secureapis_free_config(void* config);
    int secureapis_check_request(void* config, const char* method, const char* url,
                                const char* headers, const char* body, const char* ip,
                                char* output, size_t output_size);
    void secureapis_free_string(char* str);
}

class SecureAPIs : public Napi::ObjectWrap<SecureAPIs> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports);
    SecureAPIs(const Napi::CallbackInfo& info);

private:
    Napi::Value CheckRequest(const Napi::CallbackInfo& info);
    Napi::Value GetVersion(const Napi::CallbackInfo& info);

    void* config_;
};

Napi::Object SecureAPIs::Init(Napi::Env env, Napi::Object exports) {
    Napi::Function func = DefineClass(env, "SecureAPIs", {
        InstanceMethod("checkRequest", &SecureAPIs::CheckRequest),
        InstanceMethod("getVersion", &SecureAPIs::GetVersion)
    });

    exports.Set("SecureAPIs", func);
    return exports;
}

SecureAPIs::SecureAPIs(const Napi::CallbackInfo& info)
    : Napi::ObjectWrap<SecureAPIs>(info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1 || !info[0].IsObject()) {
        Napi::TypeError::New(env, "Configuration object expected").ThrowAsJavaScriptException();
        return;
    }

    Napi::Object configObj = info[0].As<Napi::Object>();

    // Build JSON config string
    std::string json = "{";
    bool first = true;

    if (configObj.Has("rateLimitRequests")) {
        json += "\"rate_limit_requests\":" + std::to_string(configObj.Get("rateLimitRequests").As<Napi::Number>().Int32Value());
        first = false;
    }

    if (configObj.Has("rateLimitWindowSeconds")) {
        if (!first) json += ",";
        json += "\"rate_limit_window_seconds\":" + std::to_string(configObj.Get("rateLimitWindowSeconds").As<Napi::Number>().Int32Value());
        first = false;
    }

    if (configObj.Has("jwtSecret")) {
        if (!first) json += ",";
        std::string secret = configObj.Get("jwtSecret").As<Napi::String>().Utf8Value();
        json += "\"jwt_secret\":\"" + secret + "\"";
        first = false;
    }

    if (configObj.Has("enableInputValidation")) {
        if (!first) json += ",";
        bool enabled = configObj.Get("enableInputValidation").As<Napi::Boolean>().Value();
        json += "\"enable_input_validation\":" + std::string(enabled ? "true" : "false");
        first = false;
    }

    if (configObj.Has("enableSecurityHeaders")) {
        if (!first) json += ",";
        bool enabled = configObj.Get("enableSecurityHeaders").As<Napi::Boolean>().Value();
        json += "\"enable_security_headers\":" + std::string(enabled ? "true" : "false");
        first = false;
    }

    json += "}";

    config_ = secureapis_create_config(json.c_str());
}

Napi::Value SecureAPIs::CheckRequest(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1 || !info[0].IsObject()) {
        Napi::TypeError::New(env, "Request object expected").ThrowAsJavaScriptException();
        return env.Null();
    }

    Napi::Object requestObj = info[0].As<Napi::Object>();

    std::string method = requestObj.Get("method").As<Napi::String>().Utf8Value();
    std::string url = requestObj.Get("url").As<Napi::String>().Utf8Value();
    std::string ip = requestObj.Get("ip").As<Napi::String>().Utf8Value();

    std::string headers = "{}";
    if (requestObj.Has("headers")) {
        // Convert headers object to JSON string (simplified)
        headers = "{}"; // TODO: Implement proper headers serialization
    }

    std::string body = "";
    if (requestObj.Has("body")) {
        body = requestObj.Get("body").As<Napi::String>().Utf8Value();
    }

    // Call Rust function
    const size_t output_size = 4096;
    std::unique_ptr<char[]> output(new char[output_size]);

    int result = secureapis_check_request(config_,
                                         method.c_str(),
                                         url.c_str(),
                                         headers.c_str(),
                                         body.c_str(),
                                         ip.c_str(),
                                         output.get(),
                                         output_size);

    // Parse result
    std::string resultStr(output.get());
    Napi::Object response = Napi::Object::New(env);

    if (result == 0) {
        response.Set("allowed", Napi::Boolean::New(env, true));
        response.Set("reason", Napi::String::New(env, ""));
    } else {
        response.Set("allowed", Napi::Boolean::New(env, false));
        response.Set("reason", Napi::String::New(env, resultStr));
    }

    return response;
}

Napi::Value SecureAPIs::GetVersion(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    return Napi::String::New(env, "1.0.0");
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    return SecureAPIs::Init(env, exports);
}

NODE_API_MODULE(secureapis, Init)