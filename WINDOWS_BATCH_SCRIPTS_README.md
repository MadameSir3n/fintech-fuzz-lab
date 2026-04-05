# Windows Batch Scripts for FinTech Fuzz Lab 🪟🔍

This directory contains Windows batch scripts for running the FinTech Fuzz Lab on Windows systems.

## Available Scripts

### 1. `start_fuzzing.bat`
**Basic version** - Simple script that replicates the functionality of the bash script.

**Usage:**
```cmd
start_fuzzing.bat
```

**Features:**
- Docker status checking
- Container building and startup
- API health check
- Fuzz test execution
- Automatic cleanup

### 2. `start_fuzzing_advanced.bat`
**Advanced version** - Enhanced script with additional features and options.

**Usage:**
```cmd
start_fuzzing_advanced.bat [OPTIONS]
```

**Options:**
- `--verbose` - Enable verbose output from fuzzer
- `--no-cleanup` - Leave containers running after completion
- `--timeout N` - Set API startup timeout (default: 10 seconds)
- `--url URL` - Specify custom API URL (default: http://localhost:8000)

**Examples:**
```cmd
# Basic usage
start_fuzzing_advanced.bat

# Verbose mode with longer timeout
start_fuzzing_advanced.bat --verbose --timeout 15

# Leave containers running for investigation
start_fuzzing_advanced.bat --no-cleanup

# Custom API URL
start_fuzzing_advanced.bat --url http://localhost:8080
```

**Advanced Features:**
- Comprehensive logging to timestamped log files
- Detailed error reporting with container logs
- Artifact counting and listing
- Configurable timeouts
- Command-line parameter support
- Better error handling and cleanup

## Prerequisites

1. **Docker Desktop** - Must be installed and running
2. **Python 3.8+** - For running the fuzzer
3. **curl** - For health checks (usually included with Windows 10/11)

## File Structure

```
fintech-fuzz-lab/
├── start_fuzzing.bat          # Basic batch script
├── start_fuzzing_advanced.bat # Advanced batch script
├── start_fuzzing.sh           # Original bash script
├── WINDOWS_BATCH_SCRIPTS_README.md
└── ...other project files
```

## Log Files

The advanced script creates log files in the format:
```
fuzz_lab_YYYYMMDD_HHMM.log
```

Logs contain:
- Timestamps for all operations
- Docker version information
- Health check results
- Fuzzer output and exit codes
- Container logs on failure
- Artifact counts

## Error Handling

Both scripts provide comprehensive error handling:
- Docker status verification
- Container build failure detection
- API health check validation
- Graceful cleanup on errors
- Detailed error messages with container logs

## Comparison with Bash Script

| Feature | Bash Script | Basic Batch | Advanced Batch |
|---------|-------------|-------------|----------------|
| Docker check | ✅ | ✅ | ✅ |
| Container management | ✅ | ✅ | ✅ |
| Health check | ✅ | ✅ | ✅ |
| Fuzzer execution | ✅ | ✅ | ✅ |
| Logging | ❌ | ❌ | ✅ |
| Command-line options | ❌ | ❌ | ✅ |
| Artifact counting | ✅ | ✅ | ✅ |
| Error logging | ❌ | ❌ | ✅ |
| Configurable timeout | ❌ | ❌ | ✅ |

## Troubleshooting

### Common Issues:

1. **Docker not running**
   - Start Docker Desktop before running the script

2. **Port 8000 already in use**
   - Stop other services using port 8000
   - Use `--url` option with a different port

3. **Python not found**
   - Ensure Python is installed and in PATH
   - Run from activated virtual environment if using one

4. **curl not available**
   - Install curl or use Windows 10/11 which includes it
   - Alternatively, install via Chocolatey: `choco install curl`

### Debug Mode:
For troubleshooting, run with verbose output:
```cmd
start_fuzzing_advanced.bat --verbose --no-cleanup
```

This will show detailed output and leave containers running for investigation.

## Integration with CI/CD

The batch scripts can be integrated into Windows-based CI/CD pipelines. The advanced script's logging and exit codes make it suitable for automated testing environments.

Example GitHub Actions step:
```yaml
- name: Run FinTech Fuzz Tests
  run: .\fintech-fuzz-lab\start_fuzzing_advanced.bat --timeout 20
```

## License

Same as the main FinTech Fuzz Lab project - see main LICENSE file.