# FinTech Fuzz Lab

An automated security testing harness that fuzzes a payment API with thousands of adversarial inputs — SQL injection, XSS, malformed JSON, oversized payloads — to surface vulnerabilities before deployment.

---

## Problem

Payment APIs are a top target for attackers. Most teams only test happy-path inputs, leaving edge cases — malformed JSON, boundary-busting numbers, injection strings — undiscovered until something breaks in production.

## Solution

This lab wraps a realistic FastAPI payment endpoint in a Hypothesis-powered fuzz harness that automatically generates thousands of attack inputs across multiple categories and saves any inputs that cause unexpected behavior as reproducible artifacts.

## Key Features

- Property-based testing via Hypothesis (intelligent generation, not random noise)
- Attack categories: SQL injection, XSS, type confusion, boundary values, oversized payloads
- Artifacts saved automatically for every failing case
- Realistic payment API endpoint as the test target
- Full pytest integration — runs in CI with no extra setup
- Docker support for isolated testing environments

## Tech Stack

- **Python** — test harness and API
- **FastAPI** — payment API target
- **Hypothesis** — property-based fuzzing engine
- **pytest** — test runner
- **Docker / Docker Compose** — isolated test environment

## Example Flow

```
1. Hypothesis generates: card_number = "'; DROP TABLE payments; --"
2. POST /payments  →  { "card_number": "...", "amount": 100.00, ... }
3. API returns 422 (validation caught it)  →  PASS

4. Hypothesis generates: amount = -9999999999999.99
5. POST /payments  →  server error 500  →  FAIL
6. Artifact saved: artifacts/boundary_amount_1710512345.json
7. Review artifact → fix the validator → rerun
```

## How to Run

```bash
git clone https://github.com/MadameSir3n/fintech-fuzz-lab.git
cd fintech-fuzz-lab
pip install -r requirements.txt
python main.py        # start the payment API at http://localhost:8000
```

Run fuzz tests:

```bash
python -m pytest tests/ -v
```

Or with Docker:

```bash
docker-compose up --build
```

## Known Limitations

- Intentionally vulnerable endpoints are for local testing only — do not deploy publicly
- Some components are still being refined
- This is an active development system

## Sample Test Output

```
tests/test_payment_api.py::test_valid_payment PASSED
tests/test_payment_api.py::test_invalid_card_number PASSED
tests/test_payment_api.py::test_negative_amount PASSED
tests/test_payment_api.py::test_sql_injection PASSED
tests/test_payment_api.py::test_xss_in_merchant_id PASSED
tests/test_payment_api.py::test_oversized_payload PASSED
tests/test_payment_api.py::test_card_number_property PASSED    (100 examples)

25 passed in 3.28s
```

## Why This Matters

Security vulnerabilities in payment systems cause direct financial harm. This project demonstrates how property-based fuzzing can be applied to financial APIs to systematically discover input handling flaws — the same technique used by security engineers at scale, automated into a repeatable test suite.

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