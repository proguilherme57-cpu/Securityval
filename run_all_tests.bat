@echo off
REM Master test script for all SecureAPIs language bindings

echo ========================================
echo SecureAPIs Language Bindings Test Suite
echo ========================================
echo.

set TOTAL_TESTS=0
set PASSED_TESTS=0

REM Test C# bindings
echo Testing C# bindings...
echo ======================
if exist bindings\csharp (
    cd bindings\csharp
    dotnet test --verbosity minimal
    if %errorlevel% equ 0 (
        echo ✓ C# tests passed
        set /a PASSED_TESTS+=1
    ) else (
        echo ✗ C# tests failed
    )
    set /a TOTAL_TESTS+=1
    cd ..\..
) else (
    echo ⚠ C# bindings not found, skipping tests
)
echo.

REM Test Java bindings
echo Testing Java bindings...
echo =======================
if exist bindings\java (
    cd bindings\java
    mvn test -q
    if %errorlevel% equ 0 (
        echo ✓ Java tests passed
        set /a PASSED_TESTS+=1
    ) else (
        echo ✗ Java tests failed
    )
    set /a TOTAL_TESTS+=1
    cd ..\..
) else (
    echo ⚠ Java bindings not found, skipping tests
)
echo.

REM Test Node.js bindings
echo Testing Node.js bindings...
echo ==========================
if exist bindings\nodejs (
    cd bindings\nodejs
    npm test
    if %errorlevel% equ 0 (
        echo ✓ Node.js tests passed
        set /a PASSED_TESTS+=1
    ) else (
        echo ✗ Node.js tests failed
    )
    set /a TOTAL_TESTS+=1
    cd ..\..
) else (
    echo ⚠ Node.js bindings not found, skipping tests
)
echo.

REM Test Python bindings
echo Testing Python bindings...
echo =========================
if exist bindings\python (
    cd bindings\python
    python test_secureapis.py
    if %errorlevel% equ 0 (
        echo ✓ Python tests passed
        set /a PASSED_TESTS+=1
    ) else (
        echo ✗ Python tests failed
    )
    set /a TOTAL_TESTS+=1
    cd ..\..
) else (
    echo ⚠ Python bindings not found, skipping tests
)
echo.

echo ========================================
echo Test Results: %PASSED_TESTS%/%TOTAL_TESTS% test suites passed
echo ========================================

if %PASSED_TESTS% equ %TOTAL_TESTS% (
    if %TOTAL_TESTS% gtr 0 (
        echo 🎉 All tests passed!
    ) else (
        echo ⚠ No test suites were found to run
    )
) else (
    echo ⚠️ Some tests failed. Check the output above.
    echo Individual binding test results are shown above.
)

echo.
echo Test run completed.
echo ========================================