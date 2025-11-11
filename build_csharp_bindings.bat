@echo off
REM Build script for SecureAPIs C# bindings

echo Building SecureAPIs Rust library for Windows...

REM Build Rust library as DLL (stay in current directory)
cargo build --release

if %errorlevel% neq 0 (
    echo Failed to build Rust library
    exit /b 1
)

REM Copy the DLL to the C# project
copy target\release\secureapis.dll bindings\csharp\runtimes\win-x64\native\

if %errorlevel% neq 0 (
    echo Failed to copy DLL
    exit /b 1
)

echo Building C# package...
cd bindings\csharp
dotnet build --configuration Release

if %errorlevel% neq 0 (
    echo Failed to build C# package
    exit /b 1
)

echo Build complete!
echo.
echo To use in your .NET project:
echo 1. Reference the SecureAPIs.dll
echo 2. Add to your middleware pipeline:
echo    app.UseSecureAPIs();