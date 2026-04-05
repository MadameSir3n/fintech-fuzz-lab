@echo off
chcp 65001 >nul
echo.
echo 🧪 Testing FinTech Fuzz Lab Windows Setup
echo ========================================
echo.

echo 1. Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found
    exit /b 1
)
echo ✅ Python found
echo.

echo 2. Checking Docker...
docker --version
if %errorlevel% neq 0 (
    echo ❌ Docker not found
    exit /b 1
)
echo ✅ Docker found
echo.

echo 3. Testing Python module imports...
python -c "import src.app; print('✅ App module imports successfully')"
if %errorlevel% neq 0 (
    echo ❌ App module import failed
    exit /b 1
)
echo ✅ App module imports successfully
echo.

echo 4. Testing Fuzzer module...
python -c "import src.fuzzer; print('✅ Fuzzer module imports successfully')"
if %errorlevel% neq 0 (
    echo ❌ Fuzzer module import failed
    exit /b 1
)
echo ✅ Fuzzer module imports successfully
echo.

echo 5. Testing Fuzzer CLI...
python -m src.fuzzer --help
if %errorlevel% neq 0 (
    echo ❌ Fuzzer CLI failed
    exit /b 1
)
echo ✅ Fuzzer CLI works
echo.
echo ========================================
echo ✅ ALL TESTS PASSED!
echo.
echo The FinTech Fuzz Lab is ready for use on Windows.
echo.
echo Run the following commands to start fuzzing:
echo   start_fuzzing.bat         - Basic version
echo   start_fuzzing_advanced.bat - Advanced version with logging
echo.
exit /b 0