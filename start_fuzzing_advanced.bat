@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Configuration
set LOG_FILE=fuzz_lab_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%.log
set API_URL=http://localhost:8000
set ARTIFACTS_DIR=artifacts

REM Parse command line arguments
set VERBOSE=0
set NO_CLEANUP=0
set TIMEOUT=10

:parse_args
if "%~1"=="" goto args_done
if "%~1"=="--verbose" set VERBOSE=1
if "%~1"=="--no-cleanup" set NO_CLEANUP=1
if "%~1"=="--timeout" (
    set TIMEOUT=%~2
    shift
)
if "%~1"=="--url" (
    set API_URL=%~2
    shift
)
shift
goto parse_args

:args_done

echo ================================
echo 🚀 FinTech Fuzz Lab - Windows Batch Script
echo ================================
echo Log file: !LOG_FILE!
echo API URL: !API_URL!
echo Timeout: !TIMEOUT! seconds
echo.

REM Redirect output to log file
if "!VERBOSE!" equ "0" (
    >"!LOG_FILE!" (
        echo FinTech Fuzz Lab Session - %date% %time%
        echo ================================
    )
)

REM Check if Docker is installed and running
echo Checking Docker status...
for /f "tokens=*" %%i in ('docker --version 2^>^&1') do (
    echo Docker version: %%i
    >>"!LOG_FILE!" echo Docker version: %%i
)

for /f "tokens=*" %%i in ('docker info 2^>^&1') do (
    echo | find "Cannot connect" >nul
    if !errorlevel! equ 0 (
        echo ❌ ERROR: Docker is not running. Please start Docker Desktop.
        >>"!LOG_FILE!" echo ERROR: Docker is not running
        exit /b 1
    )
)

echo ✅ Docker is running
echo.

REM Build and start containers
echo 🐳 Building and starting Docker containers...
>>"!LOG_FILE!" echo Building containers: %date% %time%

docker-compose up --build -d

if !errorlevel! neq 0 (
    echo ❌ ERROR: Failed to build/start Docker containers
    >>"!LOG_FILE!" echo ERROR: Docker compose failed
    goto cleanup
)

echo ✅ Containers started successfully
echo ⏳ Waiting for API to start (!TIMEOUT! seconds)...
>>"!LOG_FILE!" echo Waiting for API: %date% %time%

timeout /t !TIMEOUT! /nobreak >nul

REM Health check
echo 🧪 Running health check...
>>"!LOG_FILE!" echo Health check: %date% %time%

curl -f "!API_URL!/health"
if !errorlevel! neq 0 (
    echo ❌ ERROR: API health check failed
    >>"!LOG_FILE!" echo ERROR: Health check failed
    echo.
    echo 📋 Checking container logs...
    docker-compose logs fintech-fuzz-api
    >>"!LOG_FILE!" echo Container logs:
    docker-compose logs fintech-fuzz-api >>"!LOG_FILE!" 2^>^&1
    goto cleanup
)

echo ✅ API is healthy!
echo.

REM Run fuzzer
echo 🎯 Starting fuzz tests...
echo ================================
echo.
>>"!LOG_FILE!" echo Starting fuzz tests: %date% %time%

if "!VERBOSE!" equ "1" (
    python -m src.fuzzer --url "!API_URL!" --verbose
) else (
    python -m src.fuzzer --url "!API_URL!"
)

set FUZZ_RESULT=!errorlevel!
>>"!LOG_FILE!" echo Fuzz test completed with exit code: !FUZZ_RESULT!

echo.
echo ================================
echo 🧪 Fuzz testing completed!
echo.

REM Count artifacts
set ARTIFACT_COUNT=0
if exist "!ARTIFACTS_DIR!\*" (
    for /f %%i in ('dir /b "!ARTIFACTS_DIR!\" 2^>nul ^| find /c /v ""') do set ARTIFACT_COUNT=%%i
)

if !FUZZ_RESULT! equ 0 (
    echo ✅ SUCCESS: No crashes detected - API handled all test cases
    >>"!LOG_FILE!" echo SUCCESS: No crashes detected
) else (
    echo ⚠️  WARNING: Crashes detected - check artifacts directory
    echo    Saved artifacts: !ARTIFACT_COUNT! files
    >>"!LOG_FILE!" echo WARNING: Crashes detected, artifacts: !ARTIFACT_COUNT!
)

echo.
echo 📊 API is running at: !API_URL!
echo 📚 API documentation: !API_URL!/docs
echo 📁 Artifacts directory: !ARTIFACTS_DIR!\
echo 📄 Log file: !LOG_FILE!
echo.

REM Display recent artifacts if any
if !ARTIFACT_COUNT! gtr 0 (
    echo 📋 Recent artifacts:
    for /f "tokens=*" %%f in ('dir /b "!ARTIFACTS_DIR!\*" 2^>nul ^| head -5') do (
        echo    - %%f
    )
    echo.
)

if "!NO_CLEANUP!" equ "1" (
    echo 💡 Containers left running (--no-cleanup specified)
    echo    Run 'docker-compose down' to stop them later
    >>"!LOG_FILE!" echo Containers left running per --no-cleanup
) else (
    echo 💡 Press any key to stop containers and exit...
    pause >nul
    >>"!LOG_FILE!" echo User stopped containers: %date% %time%
    
    echo.
    echo 🛑 Stopping Docker containers...
    docker-compose down
    >>"!LOG_FILE!" echo Containers stopped: %date% %time%
)

echo.
echo ✅ FinTech Fuzz Lab session completed!
>>"!LOG_FILE!" echo Session completed: %date% %time%

echo ================================
exit /b 0

:cleanup
if "!NO_CLEANUP!" equ "1" (
    echo 💡 Containers left running for investigation
    >>"!LOG_FILE!" echo Containers left running after error
) else (
    echo 🛑 Cleaning up Docker containers...
    docker-compose down
    >>"!LOG_FILE!" echo Cleanup completed: %date% %time%
)
exit /b 1