#!/usr/bin/env python3
"""
FinTech Fuzz Lab - Hypothesis-based fuzzer harness

A comprehensive fuzzing tool for testing financial APIs with various attack vectors
including malformed JSON, oversized payloads, SQL injection, and other security tests.
"""

import hypothesis
from hypothesis import strategies as st
from hypothesis import given, settings, HealthCheck
import requests
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinTechFuzzer:
    """Fuzzer for financial API security testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.results = {
            "total_tests": 0,
            "crashes": 0,
            "errors": 0,
            "warnings": 0,
            "successful": 0,
            "start_time": datetime.now(),
            "end_time": None,
            "artifacts": []
        }
        self.artifacts_dir = "../artifacts"
        os.makedirs(self.artifacts_dir, exist_ok=True)
    
    def save_artifact(self, test_type: str, payload: Any, response: Any, error: str = None):
        """Save a test artifact for later analysis."""
        artifact = {
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type,
            "payload": payload,
            "response": response,
            "error": error
        }
        
        # Save to file
        filename = f"{test_type}_{int(datetime.now().timestamp() * 1000)}.json"
        filepath = os.path.join(self.artifacts_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(artifact, f, indent=2, default=str)
        
        self.results["artifacts"].append({
            "filename": filename,
            "test_type": test_type,
            "timestamp": artifact["timestamp"]
        })
        
        return artifact
    
    def test_endpoint(self, endpoint: str, method: str = "POST", payload: Any = None, 
                     headers: Dict[str, str] = None):
        """Test an endpoint and record results."""
        self.results["total_tests"] += 1
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            elif method.upper() == "GET":
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                response = requests.request(method, url, json=payload, headers=headers, timeout=10)
            
            # Check for error responses
            if response.status_code >= 500:
                self.results["errors"] += 1
                artifact = self.save_artifact(
                    "server_error", 
                    payload, 
                    {"status_code": response.status_code, "text": response.text},
                    f"Server error: {response.status_code}"
                )
                logger.warning(f"Server error {response.status_code} on {endpoint}")
                
            elif response.status_code >= 400:
                self.results["warnings"] += 1
                # Don't save artifacts for normal client errors
                
            else:
                self.results["successful"] += 1
                
            return response
            
        except requests.exceptions.RequestException as e:
            self.results["crashes"] += 1
            artifact = self.save_artifact(
                "crash", 
                payload, 
                None, 
                f"Request failed: {str(e)}"
            )
            logger.error(f"Crash on {endpoint}: {str(e)}")
            return None
        except Exception as e:
            self.results["crashes"] += 1
            artifact = self.save_artifact(
                "crash", 
                payload, 
                None, 
                f"Unexpected error: {str(e)}"
            )
            logger.error(f"Unexpected error on {endpoint}: {str(e)}")
            return None
    
    # Strategy generators for different attack vectors
    
    @staticmethod
    def malformed_json_strategy():
        """Generate malformed JSON payloads."""
        return st.one_of(
            st.just(''),  # Empty string
            st.just('{'),  # Incomplete JSON
            st.just('}'),  # Incomplete JSON
            st.just('{"test":'),  # Missing value
            st.just('{"test"}'),  # Missing colon
            st.just('{"test": undefined}'),  # Invalid value
            st.just('{"test": NaN}'),  # Invalid value
            st.just('{"test": Infinity}'),  # Invalid value
            st.text(min_size=1000, max_size=10000),  # Large text
            st.binary(min_size=1000, max_size=10000),  # Binary data
        )
    
    @staticmethod
    def sql_injection_strategy():
        """Generate SQL injection payloads."""
        sql_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' UNION SELECT NULL --",
            "; DROP TABLE users; --",
            "' OR 1=1; --",
            "' UNION SELECT username, password FROM users --",
            "' OR EXISTS(SELECT * FROM users) --",
            "' OR (SELECT COUNT(*) FROM users) > 0 --",
            "' OR ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 0 --",
            "' OR BENCHMARK(1000000,MD5('test')) --"
        ]
        return st.sampled_from(sql_payloads)
    
    @staticmethod
    def xss_strategy():
        """Generate XSS payloads."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<meta http-equiv=\"refresh\" content=\"0;url=javascript:alert('XSS')\">",
            "<object data=javascript:alert('XSS')>",
            "<embed src=javascript:alert('XSS')>",
            "';\"><script>alert('XSS')</script>"
        ]
        return st.sampled_from(xss_payloads)
    
    @staticmethod
    def oversized_payload_strategy():
        """Generate oversized payloads."""
        return st.dictionaries(
            keys=st.text(min_size=10, max_size=100),
            values=st.one_of(
                st.text(min_size=1000, max_size=10000),
                st.lists(st.text(min_size=100, max_size=1000), min_size=10, max_size=100),
                st.dictionaries(
                    keys=st.text(min_size=5, max_size=20),
                    values=st.text(min_size=500, max_size=5000),
                    min_size=10, max_size=50
                )
            ),
            min_size=10, max_size=100
        )
    
    @staticmethod
    def payment_payload_strategy():
        """Generate valid-looking payment payloads with fuzzed fields."""
        return st.fixed_dictionaries({
            "amount": st.one_of(
                st.floats(min_value=0.01, max_value=10000.0),
                st.just(-1.0),  # Negative amount
                st.just(0.0),   # Zero amount
                st.just(1000000.0),  # Very large amount
            ),
            "currency": st.one_of(
                st.just("USD"),
                st.just("EUR"),
                st.just("GBP"),
                st.text(min_size=1, max_size=10),  # Invalid currency
                st.just("")  # Empty currency
            ),
            "card_number": st.one_of(
                st.just("4111111111111111"),  # Valid Visa
                st.just("5555555555554444"),  # Valid Mastercard
                st.text(min_size=13, max_size=19),  # Random numbers
                st.just("123"),  # Too short
                st.just("12345678901234567890"),  # Too long
                st.just("abcdefghijklmnop"),  # Non-numeric
            ),
            "expiry_date": st.one_of(
                st.just("12/25"),  # Valid
                st.just("13/25"),  # Invalid month
                st.just("00/25"),  # Invalid month
                st.just("12/00"),  # Invalid year
                st.text(min_size=1, max_size=10),  # Random text
            ),
            "cvv": st.one_of(
                st.just("123"),  # Valid
                st.just("12"),   # Too short
                st.just("12345"),  # Too long
                st.just("abc"),   # Non-numeric
            ),
            "merchant_id": st.text(min_size=1, max_size=50),
            "description": st.one_of(
                st.text(min_size=1, max_size=100),
                st.just(None)
            ),
            "metadata": st.one_of(
                st.dictionaries(
                    keys=st.text(min_size=1, max_size=20),
                    values=st.text(min_size=1, max_size=50),
                    min_size=0, max_size=10
                ),
                st.just(None)
            )
        })
    
    # Fuzz test methods
    
    @given(payload=malformed_json_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def fuzz_malformed_json(self, payload):
        """Fuzz test with malformed JSON payloads."""
        self.test_endpoint("/payments", "POST", payload)
    
    @given(payload=payment_payload_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def fuzz_payment_payloads(self, payload):
        """Fuzz test with various payment payload variations."""
        self.test_endpoint("/payments", "POST", payload)
    
    @given(payload=sql_injection_strategy())
    @settings(max_examples=20)
    def fuzz_sql_injection(self, payload):
        """Fuzz test with SQL injection payloads."""
        # Test in various fields
        test_payload = {
            "description": payload,
            "merchant_id": payload,
            "card_number": f"4111111111111111{payload}"
        }
        self.test_endpoint("/payments", "POST", test_payload)
    
    @given(payload=xss_strategy())
    @settings(max_examples=20)
    def fuzz_xss(self, payload):
        """Fuzz test with XSS payloads."""
        # Test in various fields
        test_payload = {
            "description": payload,
            "merchant_id": payload
        }
        self.test_endpoint("/payments", "POST", test_payload)
    
    @given(payload=oversized_payload_strategy())
    @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
    def fuzz_oversized_payloads(self, payload):
        """Fuzz test with oversized payloads."""
        self.test_endpoint("/payments", "POST", payload)
    
    def fuzz_vulnerable_endpoints(self):
        """Fuzz test the intentionally vulnerable endpoints."""
        # Test echo endpoint with various payloads
        echo_payloads = [
            "<script>alert('test')</script>",
            "' OR 1=1 --",
            "{" * 1000,  # Very large JSON
            "A" * 10000,  # Very long string
        ]
        
        for payload in echo_payloads:
            self.test_endpoint("/vulnerable/echo", "POST", payload)
            self.test_endpoint("/vulnerable/json-parse", "POST", payload)
        
        # Test reflection endpoint
        reflect_payloads = self.xss_strategy().example() + self.sql_injection_strategy().example()
        for payload in reflect_payloads:
            self.test_endpoint(f"/vulnerable/reflect?param={payload}", "GET")
    
    def run_all_tests(self):
        """Run all fuzz tests."""
        logger.info("Starting FinTech Fuzz Lab tests...")
        
        try:
            # Run hypothesis-based tests
            self.fuzz_malformed_json()
            self.fuzz_payment_payloads()
            self.fuzz_sql_injection()
            self.fuzz_xss()
            self.fuzz_oversized_payloads()
            
            # Run additional tests
            self.fuzz_vulnerable_endpoints()
            
        except Exception as e:
            logger.error(f"Fuzz test execution failed: {e}")
        
        # Finalize results
        self.results["end_time"] = datetime.now()
        duration = (self.results["end_time"] - self.results["start_time"]).total_seconds()
        self.results["duration_seconds"] = duration
        
        # Save summary
        summary_path = os.path.join(self.artifacts_dir, "fuzz_test_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("FIN TECH FUZZ LAB - TEST SUMMARY")
        logger.info("="*50)
        logger.info(f"Total tests run: {self.results['total_tests']}")
        logger.info(f"Successful responses: {self.results['successful']}")
        logger.info(f"Server errors (5xx): {self.results['errors']}")
        logger.info(f"Client errors (4xx): {self.results['warnings']}")
        logger.info(f"Crashes/exceptions: {self.results['crashes']}")
        logger.info(f"Artifacts saved: {len(self.results['artifacts'])}")
        logger.info(f"Test duration: {duration:.2f} seconds")
        logger.info("="*50)
        
        return self.results

def main():
    """Main entry point for the fuzzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FinTech Fuzz Lab - Security Testing Harness")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the API to test")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    fuzzer = FinTechFuzzer(base_url=args.url)
    results = fuzzer.run_all_tests()
    
    # Exit with error code if crashes were detected
    if results["crashes"] > 0:
        return 1
    return 0

if __name__ == "__main__":
    exit(main())