@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo 🚀 Starting FinTech Fuzz Lab...
echo ================================
echo.

REM Check if Docker is running
for /f "tokens=*" %%i in ('docker info 2^>^&1') do (
    echo | find "Cannot connect" >nul
    if !errorlevel! equ 0 (
        echo ❌ Docker is not running. Please start Docker and try again.
        exit /b 1
    )
)

echo 🐳 Building and starting Docker containers...
docker-compose up --build -d

if !errorlevel! neq 0 (
    echo ❌ Failed to start Docker containers
    exit /b 1
)

echo ⏳ Waiting for API to start...
timeout /t 10 /nobreak >nul

echo 🧪 Running health check...
curl -f http://localhost:8000/health
if !errorlevel! neq 0 (
    echo ❌ API health check failed
    echo.
    echo 📋 Checking container logs...
    docker-compose logs fintech-fuzz-api
    exit /b 1
)

echo ✅ API is healthy!
echo.
echo 🎯 Starting fuzz tests...
echo ================================
echo.

REM Run the fuzzer
python -m src.fuzzer --url http://localhost:8000 --verbose
set FUZZ_RESULT=!errorlevel!

echo.
echo ================================
echo 🧪 Fuzz testing completed!
echo.

if !FUZZ_RESULT! equ 0 (
    echo ✅ No crashes detected - API handled all test cases
) else (
    echo ⚠️  Crashes detected - check artifacts\ directory for details
    for /f %%i in ('dir /b artifacts\ 2^>nul ^| find /c /v ""') do set ARTIFACT_COUNT=%%i
    echo    Saved artifacts: !ARTIFACT_COUNT! files
)

echo.
echo 📊 API is running at: http://localhost:8000
echo 📚 API documentation: http://localhost:8000/docs
echo 📁 Artifacts directory: .\artifacts\
echo.
echo 💡 Press any key to stop the containers and exit...
pause >nul

echo.
echo 🛑 Stopping Docker containers...
docker-compose down

echo.
echo ✅ FinTech Fuzz Lab session completed!
exit /b 0