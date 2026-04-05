#!/usr/bin/env python3
"""
Test suite for FinTech Fuzz Lab payment API

Includes unit tests, integration tests, and security test examples.
"""

import asyncio
import pytest
import json
import httpx
from src.app import app, PaymentRequest
from hypothesis import given, strategies as st
import hypothesis


class _SyncClient:
    """Thin synchronous wrapper around httpx.AsyncClient + ASGITransport."""

    def get(self, url, **kwargs):
        return asyncio.run(self._call("get", url, **kwargs))

    def post(self, url, **kwargs):
        return asyncio.run(self._call("post", url, **kwargs))

    async def _call(self, method, url, **kwargs):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            return await getattr(c, method)(url, **kwargs)


# Drop-in replacement for TestClient
client = _SyncClient()

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_valid_payment():
    """Test valid payment processing."""
    valid_payload = {
        "amount": 100.0,
        "currency": "USD",
        "card_number": "4111111111111111",  # Test Visa
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant_001",
        "description": "Test payment"
    }
    
    response = client.post("/payments", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["transaction_id"] is not None
    assert data["amount"] == 100.0
    assert data["currency"] == "USD"

def test_invalid_card_number():
    """Test payment with invalid card number."""
    invalid_payload = {
        "amount": 100.0,
        "currency": "USD",
        "card_number": "1234567890123456",  # Invalid card
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant_001"
    }
    
    response = client.post("/payments", json=invalid_payload)
    assert response.status_code in [400, 422]

def test_negative_amount():
    """Test payment with negative amount."""
    negative_payload = {
        "amount": -50.0,
        "currency": "USD",
        "card_number": "4111111111111111",
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant_001"
    }
    
    response = client.post("/payments", json=negative_payload)
    assert response.status_code in [400, 422]

def test_missing_required_fields():
    """Test payment with missing required fields."""
    incomplete_payload = {
        "amount": 100.0,
        "currency": "USD",
        # Missing card_number, expiry_date, cvv, merchant_id
    }
    
    response = client.post("/payments", json=incomplete_payload)
    assert response.status_code == 422  # Pydantic validation error

def test_get_payment():
    """Test retrieving a payment transaction."""
    # First create a payment
    create_payload = {
        "amount": 50.0,
        "currency": "USD",
        "card_number": "5555555555554444",  # Test Mastercard
        "expiry_date": "06/26",
        "cvv": "456",
        "merchant_id": "test_merchant_002"
    }
    
    create_response = client.post("/payments", json=create_payload)
    assert create_response.status_code == 200
    transaction_id = create_response.json()["transaction_id"]
    
    # Then retrieve it
    get_response = client.get(f"/payments/{transaction_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["amount"] == 50.0
    assert data["merchant_id"] == "test_merchant_002"

def test_list_payments():
    """Test listing payment transactions."""
    response = client.get("/payments?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_vulnerable_echo_endpoint():
    """Test the vulnerable echo endpoint."""
    test_data = "<script>alert('test')</script>"
    response = client.post("/vulnerable/echo", content=test_data)
    assert response.status_code == 200
    assert "echo" in response.json()

def test_vulnerable_json_parse():
    """Test the vulnerable JSON parse endpoint."""
    # Test with valid JSON
    valid_json = '{"test": "value"}'
    response = client.post("/vulnerable/json-parse", content=valid_json)
    assert response.status_code == 200
    
    # Test with invalid JSON
    invalid_json = '{"test":}'
    response = client.post("/vulnerable/json-parse", content=invalid_json)
    assert response.status_code == 200
    assert "error" in response.json()

def test_reflect_endpoint():
    """Test the parameter reflection endpoint."""
    test_param = "<script>alert('xss')</script>"
    response = client.get(f"/vulnerable/reflect?param={test_param}")
    assert response.status_code == 200
    assert "reflected" in response.json()

# Hypothesis-based property tests

@given(st.floats(min_value=0.01, max_value=10000.0))
def test_amount_validation_property(amount):
    """Property test for amount validation."""
    payload = {
        "amount": amount,
        "currency": "USD",
        "card_number": "4111111111111111",
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant_property"
    }
    
    response = client.post("/payments", json=payload)
    # Should either succeed or fail with validation error, but not crash
    assert response.status_code in [200, 400]

@given(st.text(min_size=13, max_size=19))
def test_card_number_property(card_number):
    """Property test for card number validation."""
    payload = {
        "amount": 100.0,
        "currency": "USD",
        "card_number": card_number,
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant_property"
    }
    
    response = client.post("/payments", json=payload)
    # Should either succeed or fail with validation error, but not crash
    assert response.status_code in [200, 400, 422]

# Edge case tests

def test_very_large_amount():
    """Test with a very large amount."""
    payload = {
        "amount": 1000000000.0,  # 1 billion
        "currency": "USD",
        "card_number": "4111111111111111",
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant_large"
    }
    
    response = client.post("/payments", json=payload)
    # Should handle large amounts without crashing
    assert response.status_code in [200, 400]

def test_empty_string_fields():
    """Test with empty string values."""
    payload = {
        "amount": 100.0,
        "currency": "",
        "card_number": "",
        "expiry_date": "",
        "cvv": "",
        "merchant_id": ""
    }
    
    response = client.post("/payments", json=payload)
    # Should return validation errors, not crash
    assert response.status_code == 422

def test_sql_injection_attempt():
    """Test with SQL injection payload."""
    payload = {
        "amount": 100.0,
        "currency": "USD",
        "card_number": "4111111111111111",
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant",
        "description": "' OR 1=1 --"  # SQL injection
    }
    
    response = client.post("/payments", json=payload)
    # Should handle gracefully without crashing
    assert response.status_code in [200, 400]

def test_xss_attempt():
    """Test with XSS payload."""
    payload = {
        "amount": 100.0,
        "currency": "USD",
        "card_number": "4111111111111111",
        "expiry_date": "12/25",
        "cvv": "123",
        "merchant_id": "test_merchant",
        "description": "<script>alert('XSS')</script>"  # XSS
    }
    
    response = client.post("/payments", json=payload)
    # Should handle gracefully without crashing
    assert response.status_code in [200, 400]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])