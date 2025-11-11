@echo off
REM Build script for SecureAPIs C# Example Application

echo Building SecureAPIs C# Example Application...
echo ==============================================

REM Build the Rust library first
echo.
echo Building Rust library...
cd ..\..
cargo build --release
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Rust library
    exit /b 1
)

REM Build the C# bindings
echo.
echo Building C# bindings...
call build_csharp_bindings.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to build C# bindings
    exit /b 1
)

REM Build the example application
echo.
echo Building example application...
cd examples\csharp
dotnet build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build example application
    exit /b 1
)

echo.
echo ==============================================
echo Build completed successfully!
echo.
echo To run the example:
echo   cd examples\csharp
echo   dotnet run
echo.
echo To test the example:
echo   .\test_example.ps1
echo ==============================================