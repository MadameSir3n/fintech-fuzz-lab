# FinTech Fuzz Lab Portfolio Case Study

FinTech Fuzz Lab is a Python security testing project focused on API input validation, property-based fuzzing, and reproducible failure analysis for payment-style workflows. It uses a FastAPI target and Hypothesis-based tests to explore how financial API endpoints behave under malformed, adversarial, oversized, and edge-case inputs.

This document is written for recruiters, hiring managers, and technical reviewers who want a quick view of what the project demonstrates.

## What This Project Demonstrates

- Building a FastAPI-style API target for security testing practice
- Using property-based testing concepts to generate broad input coverage
- Designing fuzz tests around injection strings, type confusion, boundary values, malformed JSON, and oversized payloads
- Thinking in terms of reproducible failure artifacts rather than one-off manual testing
- Applying security-testing habits to fintech/payment-style workflows
- Writing a project that connects API development, security testing, test automation, and documentation

## Why It Matters

Financial and payment APIs need strong validation because small input-handling mistakes can create reliability, fraud, or security problems. This project demonstrates a practical way to test those assumptions repeatedly instead of relying only on happy-path manual checks.

This is relevant to application security, QA automation, backend testing, fraud/risk tooling, AI-assisted security workflows, and junior technical roles where careful test design and documentation matter.

## Skill Areas Represented

### API and Backend Testing

- FastAPI-oriented API behavior
- Request validation thinking
- Error-condition testing
- Edge-case input design
- Reproducible test workflows

### Security Testing

- Injection payload testing
- XSS-style payload testing
- Boundary and oversized input testing
- Type confusion testing
- Failure artifact thinking

### Automation and Tooling

- Python automation
- Hypothesis/property-based testing concepts
- pytest integration
- Docker-oriented test environment
- Repeatable local test setup

## Evidence Map

Useful files and folders to review:

- `README.md` - project overview and example flow
- `src/app.py` - payment API target
- `src/fuzzer.py` - fuzzing/test generation logic
- `tests/test_payment_api.py` - payment API tests
- `tests/test_fuzzer.py` - fuzzer behavior tests
- `Dockerfile` and `docker-compose.yml` - container-oriented setup
- `requirements.txt` - Python dependencies

## Portfolio Note

This is a security testing lab, not a production payment system. Its value is in demonstrating how I approach API reliability, edge-case testing, validation, documentation, and repeatable security-oriented test workflows.