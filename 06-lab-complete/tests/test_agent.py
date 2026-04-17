#!/usr/bin/env python3
"""
Production Agent Test Suite

Comprehensive testing for AI Agent deployed on Railway/Render.

Usage:
    python tests/test_agent.py
    python tests/test_agent.py --url https://my-agent.up.railway.app
    python tests/test_agent.py --stress  # Run stress tests
"""
import os
import sys
import time
import json
import argparse
import requests
from typing import Dict, List, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


class AgentTester:
    """Comprehensive test suite for Production AI Agent"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{text:^70}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
    def print_test(self, name: str, passed: bool, message: str = "", details: str = ""):
        """Print test result"""
        icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"{icon} {name:.<55} {status}")
        
        if message:
            print(f"  {CYAN}→ {message}{RESET}")
        if details:
            print(f"  {YELLOW}Details: {details}{RESET}")
            
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{YELLOW}⚠ WARNING: {message}{RESET}")
        self.warnings += 1
        
    # ================================================================
    # POSITIVE TESTS - Happy Path
    # ================================================================
    
    def test_health_check(self) -> Tuple[bool, str]:
        """
        Test 1: Health Check Endpoint
        
        Expected:
        - Status: 200 OK
        - Response: JSON with "status": "ok"
        - Response time: < 2 seconds
        """
        try:
            start = time.time()
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            duration = time.time() - start
            
            if response.status_code != 200:
                return False, f"Expected 200, got {response.status_code}"
                
            data = response.json()
            
            if data.get("status") != "ok":
                return False, f"Status is '{data.get('status')}', expected 'ok'"
                
            if duration > 2:
                self.print_warning(f"Slow response: {duration:.2f}s")
                
            return True, f"Response time: {duration:.2f}s"
            
        except requests.exceptions.Timeout:
            return False, "Request timeout (> 5s)"
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def test_readiness_check(self) -> Tuple[bool, str]:
        """
        Test 2: Readiness Check Endpoint
        
        Expected:
        - Status: 200 OK
        - Response: JSON with "ready": true
        """
        try:
            response = requests.get(
                f"{self.base_url}/ready",
                timeout=5
            )
            
            if response.status_code != 200:
                return False, f"Expected 200, got {response.status_code}"
                
            data = response.json()
            
            if not data.get("ready"):
                return False, "Service not ready"
                
            return True, "Service is ready"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def test_valid_request(self) -> Tuple[bool, str]:
        """
        Test 3: Valid API Request
        
        Expected:
        - Status: 200 OK
        - Response: JSON with "question", "answer", "model", "timestamp"
        - Answer is non-empty string
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": "What is deployment?"},
                timeout=10
            )
            
            if response.status_code != 200:
                return False, f"Expected 200, got {response.status_code}"
                
            data = response.json()
            
            # Validate response structure
            required_fields = ["question", "answer", "model", "timestamp"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                return False, f"Missing fields: {', '.join(missing)}"
                
            if not data["answer"] or len(data["answer"]) == 0:
                return False, "Empty answer"
                
            return True, f"Answer length: {len(data['answer'])} chars"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    # ================================================================
    # NEGATIVE TESTS - Error Handling
    # ================================================================
    
    def test_missing_api_key(self) -> Tuple[bool, str]:
        """
        Test 4: Missing API Key
        
        Expected:
        - Status: 401 Unauthorized or 403 Forbidden
        - Error message about missing/invalid API key
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers={"Content-Type": "application/json"},
                json={"question": "test"},
                timeout=5
            )
            
            if response.status_code not in [401, 403, 422]:
                return False, f"Expected 401/403, got {response.status_code}"
                
            return True, f"Correctly rejected with {response.status_code}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def test_invalid_api_key(self) -> Tuple[bool, str]:
        """
        Test 5: Invalid API Key
        
        Expected:
        - Status: 401 Unauthorized
        - Error message about invalid API key
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": "invalid-key-12345"
                },
                json={"question": "test"},
                timeout=5
            )
            
            if response.status_code != 401:
                return False, f"Expected 401, got {response.status_code}"
                
            return True, "Correctly rejected invalid key"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def test_empty_question(self) -> Tuple[bool, str]:
        """
        Test 6: Empty Question
        
        Expected:
        - Status: 422 Unprocessable Entity (validation error)
        - Error message about invalid input
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": ""},
                timeout=5
            )
            
            if response.status_code != 422:
                return False, f"Expected 422, got {response.status_code}"
                
            return True, "Correctly rejected empty question"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def test_missing_question_field(self) -> Tuple[bool, str]:
        """
        Test 7: Missing Question Field
        
        Expected:
        - Status: 422 Unprocessable Entity
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={},
                timeout=5
            )
            
            if response.status_code != 422:
                return False, f"Expected 422, got {response.status_code}"
                
            return True, "Correctly rejected missing field"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    # ================================================================
    # EDGE CASES - Boundary Testing
    # ================================================================
    
    def test_very_long_question(self) -> Tuple[bool, str]:
        """
        Test 8: Very Long Question (2000+ characters)
        
        Expected:
        - Status: 422 (validation error) or 200 (if accepted)
        - If 200: Response should be valid
        """
        try:
            long_question = "A" * 2500  # 2500 characters
            
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": long_question},
                timeout=10
            )
            
            if response.status_code == 422:
                return True, "Correctly rejected (too long)"
            elif response.status_code == 200:
                data = response.json()
                if "answer" in data:
                    return True, "Accepted and processed"
                return False, "Invalid response structure"
            else:
                return False, f"Unexpected status: {response.status_code}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def test_special_characters(self) -> Tuple[bool, str]:
        """
        Test 9: Special Characters in Question
        
        Expected:
        - Status: 200 OK
        - Response: Valid JSON with answer
        """
        try:
            special_question = "Test with special chars: <script>alert('xss')</script> & 中文 🚀"
            
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": special_question},
                timeout=10
            )
            
            if response.status_code != 200:
                return False, f"Expected 200, got {response.status_code}"
                
            data = response.json()
            
            if "answer" not in data:
                return False, "Missing answer field"
                
            return True, "Handled special characters correctly"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def test_sql_injection_attempt(self) -> Tuple[bool, str]:
        """
        Test 10: SQL Injection Attempt
        
        Expected:
        - Status: 200 OK (treated as normal text)
        - No database errors
        """
        try:
            sql_injection = "'; DROP TABLE users; --"
            
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": sql_injection},
                timeout=10
            )
            
            if response.status_code == 500:
                return False, "Server error (possible SQL injection vulnerability)"
                
            if response.status_code == 200:
                return True, "Safely handled SQL injection attempt"
                
            return True, f"Rejected with {response.status_code}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    # ================================================================
    # RATE LIMITING TEST
    # ================================================================
    
    def test_rate_limiting(self) -> Tuple[bool, str]:
        """
        Test 11: Rate Limiting (5 requests/minute)
        
        Expected:
        - First 5 requests: 200 OK
        - 6th request: 429 Too Many Requests
        - Retry-After header present
        """
        try:
            print(f"\n  {CYAN}Making 6 rapid requests...{RESET}")
            
            results = []
            for i in range(6):
                response = requests.post(
                    f"{self.base_url}/ask",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key
                    },
                    json={"question": f"Rate limit test {i+1}"},
                    timeout=5
                )
                
                results.append(response.status_code)
                print(f"  Request {i+1}: {response.status_code}")
                
                # Small delay to avoid network issues
                time.sleep(0.1)
                
            # Check if we got rate limited
            if 429 in results:
                first_429 = results.index(429) + 1
                return True, f"Rate limited at request #{first_429}"
            else:
                return False, "No rate limiting detected (expected 429)"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    # ================================================================
    # STRESS TEST
    # ================================================================
    
    def test_concurrent_requests(self, num_requests: int = 10) -> Tuple[bool, str]:
        """
        Test 12: Concurrent Requests
        
        Expected:
        - Some requests succeed (200)
        - Some requests rate limited (429)
        - No server errors (500)
        """
        try:
            print(f"\n  {CYAN}Sending {num_requests} concurrent requests...{RESET}")
            
            def make_request(i):
                try:
                    response = requests.post(
                        f"{self.base_url}/ask",
                        headers={
                            "Content-Type": "application/json",
                            "X-API-Key": self.api_key
                        },
                        json={"question": f"Concurrent test {i}"},
                        timeout=10
                    )
                    return response.status_code
                except Exception as e:
                    return f"Error: {str(e)}"
                    
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_requests)]
                results = [f.result() for f in as_completed(futures)]
                
            # Count status codes
            status_counts = {}
            for status in results:
                status_counts[status] = status_counts.get(status, 0) + 1
                
            print(f"  {CYAN}Results:{RESET}")
            for status, count in sorted(status_counts.items()):
                print(f"    {status}: {count} requests")
                
            # Check for server errors
            if 500 in status_counts:
                return False, f"Server errors detected: {status_counts[500]} requests"
                
            # Should have mix of 200 and 429
            if 200 in status_counts and 429 in status_counts:
                return True, "Rate limiting working under load"
            elif 200 in status_counts:
                self.print_warning("No rate limiting detected under concurrent load")
                return True, "All requests succeeded"
            else:
                return False, "No successful requests"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    # ================================================================
    # STATELESS TEST
    # ================================================================
    
    def test_stateless_design(self) -> Tuple[bool, str]:
        """
        Test 13: Stateless Design (Redis Session)
        
        This test checks if the agent is truly stateless by:
        1. Making a request
        2. Waiting a bit
        3. Making another request
        4. Both should work independently
        
        Note: Full stateless test requires restarting the server,
        which can't be done from client side.
        """
        try:
            # First request
            response1 = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": "First request"},
                timeout=10
            )
            
            if response1.status_code != 200:
                return False, f"First request failed: {response1.status_code}"
                
            # Wait a bit
            time.sleep(1)
            
            # Second request
            response2 = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": "Second request"},
                timeout=10
            )
            
            if response2.status_code != 200:
                return False, f"Second request failed: {response2.status_code}"
                
            return True, "Both requests succeeded independently"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    # ================================================================
    # PERFORMANCE TEST
    # ================================================================
    
    def test_response_time(self) -> Tuple[bool, str]:
        """
        Test 14: Response Time
        
        Expected:
        - Average response time < 2 seconds
        - No request > 5 seconds
        """
        try:
            print(f"\n  {CYAN}Measuring response times (5 requests)...{RESET}")
            
            times = []
            for i in range(5):
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/ask",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key
                    },
                    json={"question": f"Performance test {i+1}"},
                    timeout=10
                )
                duration = time.time() - start
                times.append(duration)
                
                print(f"  Request {i+1}: {duration:.2f}s")
                
                # Wait to avoid rate limiting
                time.sleep(12)  # 60s / 5 requests = 12s between requests
                
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            if max_time > 5:
                return False, f"Slow request detected: {max_time:.2f}s"
                
            if avg_time > 2:
                self.print_warning(f"Average response time is high: {avg_time:.2f}s")
                
            return True, f"Avg: {avg_time:.2f}s, Max: {max_time:.2f}s"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    # ================================================================
    # RUN ALL TESTS
    # ================================================================
    
    def run_all_tests(self, include_stress: bool = False):
        """Run all test cases"""
        
        self.print_header("PRODUCTION AGENT TEST SUITE")
        print(f"Testing: {YELLOW}{self.base_url}{RESET}")
        print(f"API Key: {YELLOW}{self.api_key[:10]}...{RESET}\n")
        
        # Basic Tests
        self.print_header("🔍 BASIC TESTS")
        
        passed, msg = self.test_health_check()
        self.print_test("Health Check", passed, msg)
        
        passed, msg = self.test_readiness_check()
        self.print_test("Readiness Check", passed, msg)
        
        passed, msg = self.test_valid_request()
        self.print_test("Valid API Request", passed, msg)
        
        # Security Tests
        self.print_header("🔐 SECURITY TESTS")
        
        passed, msg = self.test_missing_api_key()
        self.print_test("Missing API Key", passed, msg)
        
        passed, msg = self.test_invalid_api_key()
        self.print_test("Invalid API Key", passed, msg)
        
        # Validation Tests
        self.print_header("✅ VALIDATION TESTS")
        
        passed, msg = self.test_empty_question()
        self.print_test("Empty Question", passed, msg)
        
        passed, msg = self.test_missing_question_field()
        self.print_test("Missing Question Field", passed, msg)
        
        # Edge Cases
        self.print_header("⚠️  EDGE CASES")
        
        passed, msg = self.test_very_long_question()
        self.print_test("Very Long Question", passed, msg)
        
        passed, msg = self.test_special_characters()
        self.print_test("Special Characters", passed, msg)
        
        passed, msg = self.test_sql_injection_attempt()
        self.print_test("SQL Injection Attempt", passed, msg)
        
        # Rate Limiting
        self.print_header("🚦 RATE LIMITING")
        
        passed, msg = self.test_rate_limiting()
        self.print_test("Rate Limiting (5 req/min)", passed, msg)
        
        # Stateless
        self.print_header("💾 STATELESS DESIGN")
        
        passed, msg = self.test_stateless_design()
        self.print_test("Stateless Design", passed, msg)
        
        # Stress Tests (optional)
        if include_stress:
            self.print_header("💪 STRESS TESTS")
            
            passed, msg = self.test_concurrent_requests(20)
            self.print_test("Concurrent Requests", passed, msg)
            
            passed, msg = self.test_response_time()
            self.print_test("Response Time", passed, msg)
        
        # Summary
        self.print_header("📊 TEST SUMMARY")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"Total tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Warnings: {self.warnings}{RESET}")
        print(f"\nSuccess rate: {percentage:.1f}%\n")
        
        if percentage >= 90:
            print(f"{GREEN}🎉 EXCELLENT! Production ready!{RESET}")
            return 0
        elif percentage >= 70:
            print(f"{YELLOW}⚠️  GOOD, but needs improvement{RESET}")
            return 1
        else:
            print(f"{RED}❌ FAILED - Not production ready{RESET}")
            return 2


def main():
    parser = argparse.ArgumentParser(description="Test Production AI Agent")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--api-key",
        default="dev-key-change-me-in-production",
        help="API Key for authentication"
    )
    parser.add_argument(
        "--stress",
        action="store_true",
        help="Include stress tests (slower)"
    )
    
    args = parser.parse_args()
    
    tester = AgentTester(args.url, args.api_key)
    exit_code = tester.run_all_tests(include_stress=args.stress)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
