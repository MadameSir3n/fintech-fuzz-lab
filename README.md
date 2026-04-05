# FinTech Fuzz Lab 🔍💳

A security testing harness for financial APIs, designed to discover vulnerabilities through automated fuzz testing with Hypothesis and comprehensive attack vectors.

## 🎯 What Problem This Solves

Replaces reactive security testing with **proactive vulnerability discovery** that catches input validation bugs, injection vulnerabilities, and edge cases **before deployment**, reducing costly production security incidents in fintech applications.

## 🚀 Features

- **Comprehensive Fuzzing**: Multiple attack vectors (SQLi, XSS, malformed JSON, oversized payloads)
- **Hypothesis Integration**: Property-based testing with intelligent test case generation
- **FastAPI Payment API**: Realistic financial endpoint for testing
- **Artifact Collection**: Automatic saving of failing test cases for reproduction
- **Dockerized**: One-command deployment and testing
- **CI Ready**: Easy integration into development pipelines

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Fuzz Harness  │───▶│   Payment API    │───▶│   Artifact      │
│   (Hypothesis)  │    │   (FastAPI)      │    │   Collection    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Test Cases    │    │   Vulnerability  │    │   Reproducible  │
│   Generation    │    │   Discovery      │    │   Failures      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛡️ Attack Vectors Tested

### 1. Input Validation
- Malformed JSON payloads
- Type confusion attacks
- Boundary value violations
- Negative/zero/oversized amounts

### 2. Injection Attacks
- SQL injection attempts
- NoSQL injection patterns
- Command injection vectors

### 3. XSS Attacks
- Script tag injections
- Event handler manipulations
- JavaScript URI schemes

### 4. Resource Exhaustion
- Oversized payloads (up to 10MB)
- Deeply nested structures
- Array bombing attacks

### 5. Business Logic
- Invalid card numbers
- Incorrect expiry dates
- Currency manipulation
- Negative amounts

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (optional, for local development)

### One-Command Deployment
```bash
# Start the API and run fuzz tests
docker-compose up --build
```

The API will be available at `http://localhost:8000` and automatic fuzz testing will begin.

### Manual Testing
```bash
# Start the API
docker-compose up fintech-fuzz-api

# In another terminal, run fuzz tests
python -m src.fuzzer --url http://localhost:8000

# Or run specific tests
python -m src.fuzzer --url http://localhost:8000 --verbose
```

### API Endpoints

#### Payment Processing
- `POST /payments` - Process a payment transaction
- `GET /payments/{id}` - Retrieve transaction details
- `GET /payments` - List recent transactions

#### Vulnerable Endpoints (for testing)
- `POST /vulnerable/echo` - Echo raw input (vulnerable)
- `POST /vulnerable/json-parse` - Parse JSON (vulnerable)
- `GET /vulnerable/reflect` - Reflect parameter (vulnerable)

#### Health Check
- `GET /health` - API health status

## 🧪 Running Tests

### Unit Tests
```bash
pytest tests/ -v
```

### Fuzz Tests
```bash
# Run comprehensive fuzz testing
python -m src.fuzzer

# Run with custom target
python -m src.fuzzer --url http://your-api:8000

# Verbose mode with detailed logging
python -m src.fuzzer --verbose
```

### Example Test Output
```
==================================================
FIN TECH FUZZ LAB - TEST SUMMARY
==================================================
Total tests run: 245
Successful responses: 178
Server errors (5xx): 3
Client errors (4xx): 59
Crashes/exceptions: 5
Artifacts saved: 8
Test duration: 45.32 seconds
==================================================
```

## 📁 Project Structure

```
fintech-fuzz-lab/
├── src/
│   ├── app.py              # FastAPI payment application
│   └── fuzzer.py           # Hypothesis fuzz harness
├── tests/
│   └── test_payment_api.py # Unit and integration tests
├── artifacts/              # Saved test cases and results
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
PYTHONPATH=/app/src
PYTHONUNBUFFERED=1

# Fuzzer Configuration
BASE_URL=http://localhost:8000
VERBOSE=false
```

### Customizing Fuzz Tests

Modify `src/fuzzer.py` to add new attack vectors:

```python
# Add new payload strategy
def custom_attack_strategy():
    return st.text(alphabet="<>"'\"/?=&", min_size=10, max_size=100)

# Add new test method
@given(payload=custom_attack_strategy())
def fuzz_custom_attack(self, payload):
    self.test_endpoint("/payments", "POST", {"description": payload})
```

## 🎯 Use Cases

### 1. CI/CD Pipeline Integration
```yaml
# GitHub Actions example
jobs:
  security-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run fuzz tests
        run: |
          docker-compose up -d fintech-fuzz-api
          sleep 10  # Wait for API to start
          python -m src.fuzzer --url http://localhost:8000
```

### 2. Local Development Testing
```bash
# Test your local API changes
python -m src.fuzzer --url http://localhost:8000

# Generate test artifacts for analysis
ls -la artifacts/
```

### 3. Production API Testing
```bash
# Test staging/production environments
python -m src.fuzzer --url https://api.staging.example.com
```

## 📊 Metrics Collected

- **Total Tests Run**: Overall test count
- **Success Rate**: Valid responses percentage
- **Error Rate**: Server errors (5xx)
- **Warning Rate**: Client errors (4xx)
- **Crash Rate**: Unhandled exceptions
- **Test Duration**: Total execution time
- **Artifacts Saved**: Reproducible test cases

## 🛡️ Security Findings Examples

### 1. Input Validation Bugs
```json
{
  "artifact": "malformed_json_1234567890.json",
  "payload": "{\"amount\": NaN}",
  "error": "Validation error: amount must be a number"
}
```

### 2. Injection Vulnerabilities
```json
{
  "artifact": "sql_injection_1234567890.json",
  "payload": {"description": "' OR 1=1 --"},
  "response": {"status_code": 500}
}
```

### 3. Resource Exhaustion
```json
{
  "artifact": "oversized_payload_1234567890.json",
  "payload": {"metadata": {"large_field": "A" * 100000}},
  "response": {"status_code": 413}
}
```

## 🚧 Future Enhancements

- [ ] Database integration for persistent artifact storage
- [ ] GraphQL endpoint fuzzing support
- [ ] gRPC protocol fuzzing capabilities
- [ ] Automated exploit generation
- [ ] Integration with OWASP ZAP
- [ ] CI/CD pipeline templates
- [ ] Real-time dashboard for test results
- [ ] Machine learning-based test case generation

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Reporting Issues

Found a bug or have a feature request? Please open an issue on GitHub with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## 📚 Learning Resources

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/advanced/security/)
- [Property-Based Testing](https://propertesting.com/)

---

**Built with ❤️ for the fintech security community**