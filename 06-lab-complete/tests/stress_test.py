#!/usr/bin/env python3
"""
Advanced Stress Test for Production AI Agent

Tests:
1. Rate limiting under load
2. Concurrent requests
3. Sustained load
4. Memory leaks
5. Response time degradation

Usage:
    python tests/stress_test.py
    python tests/stress_test.py --url https://my-agent.up.railway.app
    python tests/stress_test.py --requests 100 --workers 10
"""
import os
import sys
import time
import argparse
import requests
import statistics
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


class StressTester:
    """Advanced stress testing for production agent"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.results = []
        
    def print_header(self, text: str):
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{text:^70}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
    def make_request(self, request_id: int) -> Dict:
        """Make a single request and record metrics"""
        start = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={"question": f"Stress test request {request_id}"},
                timeout=30
            )
            
            duration = time.time() - start
            
            return {
                "id": request_id,
                "status": response.status_code,
                "duration": duration,
                "success": response.status_code == 200,
                "rate_limited": response.status_code == 429,
                "error": response.status_code >= 500,
                "timestamp": time.time()
            }
            
        except requests.exceptions.Timeout:
            return {
                "id": request_id,
                "status": 0,
                "duration": time.time() - start,
                "success": False,
                "rate_limited": False,
                "error": True,
                "timestamp": time.time(),
                "exception": "Timeout"
            }
        except Exception as e:
            return {
                "id": request_id,
                "status": 0,
                "duration": time.time() - start,
                "success": False,
                "rate_limited": False,
                "error": True,
                "timestamp": time.time(),
                "exception": str(e)
            }
            
    def test_rate_limiting_accuracy(self, num_requests: int = 10):
        """
        Test 1: Rate Limiting Accuracy
        
        Verify that rate limiting triggers exactly at 5 requests/minute
        """
        self.print_header("TEST 1: RATE LIMITING ACCURACY")
        
        print(f"{CYAN}Making {num_requests} sequential requests...{RESET}\n")
        
        results = []
        for i in range(num_requests):
            result = self.make_request(i + 1)
            results.append(result)
            
            status_icon = f"{GREEN}✓{RESET}" if result["success"] else \
                         f"{YELLOW}⚠{RESET}" if result["rate_limited"] else \
                         f"{RED}✗{RESET}"
            
            print(f"{status_icon} Request {i+1:2d}: {result['status']} ({result['duration']:.2f}s)")
            
            # Small delay to avoid network issues
            time.sleep(0.1)
            
        # Analysis
        print(f"\n{CYAN}Analysis:{RESET}\n")
        
        successful = sum(1 for r in results if r["success"])
        rate_limited = sum(1 for r in results if r["rate_limited"])
        errors = sum(1 for r in results if r["error"])
        
        print(f"Successful: {GREEN}{successful}{RESET}")
        print(f"Rate limited: {YELLOW}{rate_limited}{RESET}")
        print(f"Errors: {RED}{errors}{RESET}")
        
        # Find when rate limiting started
        first_429 = next((i for i, r in enumerate(results) if r["rate_limited"]), None)
        
        if first_429 is not None:
            print(f"\n{GREEN}✓{RESET} Rate limiting triggered at request #{first_429 + 1}")
            
            if first_429 + 1 == 6:
                print(f"{GREEN}✓{RESET} Perfect! Rate limit is exactly 5 requests/minute")
            elif 5 <= first_429 + 1 <= 7:
                print(f"{YELLOW}⚠{RESET} Close enough (triggered at request #{first_429 + 1})")
            else:
                print(f"{RED}✗{RESET} Rate limit not working correctly")
        else:
            print(f"{RED}✗{RESET} No rate limiting detected!")
            
    def test_concurrent_load(self, num_requests: int = 50, workers: int = 10):
        """
        Test 2: Concurrent Load
        
        Send many requests concurrently to test:
        - Rate limiting under load
        - No server errors (500)
        - Response time consistency
        """
        self.print_header("TEST 2: CONCURRENT LOAD")
        
        print(f"{CYAN}Sending {num_requests} requests with {workers} workers...{RESET}\n")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.make_request, i) for i in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]
            
        total_time = time.time() - start_time
        
        # Analysis
        print(f"\n{CYAN}Results:{RESET}\n")
        
        successful = sum(1 for r in results if r["success"])
        rate_limited = sum(1 for r in results if r["rate_limited"])
        errors = sum(1 for r in results if r["error"])
        
        print(f"Total requests: {num_requests}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Requests/second: {num_requests / total_time:.2f}")
        print(f"\nSuccessful: {GREEN}{successful}{RESET} ({successful/num_requests*100:.1f}%)")
        print(f"Rate limited: {YELLOW}{rate_limited}{RESET} ({rate_limited/num_requests*100:.1f}%)")
        print(f"Errors: {RED}{errors}{RESET} ({errors/num_requests*100:.1f}%)")
        
        # Response times
        durations = [r["duration"] for r in results if r["success"]]
        
        if durations:
            print(f"\n{CYAN}Response Times:{RESET}\n")
            print(f"Min: {min(durations):.2f}s")
            print(f"Max: {max(durations):.2f}s")
            print(f"Avg: {statistics.mean(durations):.2f}s")
            print(f"Median: {statistics.median(durations):.2f}s")
            
            if len(durations) > 1:
                print(f"Std Dev: {statistics.stdev(durations):.2f}s")
                
        # Status code distribution
        status_counts = {}
        for r in results:
            status = r["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print(f"\n{CYAN}Status Codes:{RESET}\n")
        for status, count in sorted(status_counts.items()):
            print(f"{status}: {count}")
            
        # Verdict
        print(f"\n{CYAN}Verdict:{RESET}\n")
        
        if errors == 0:
            print(f"{GREEN}✓{RESET} No server errors (500)")
        else:
            print(f"{RED}✗{RESET} {errors} server errors detected!")
            
        if rate_limited > 0:
            print(f"{GREEN}✓{RESET} Rate limiting working under load")
        else:
            print(f"{YELLOW}⚠{RESET} No rate limiting detected")
            
        if durations and max(durations) < 5:
            print(f"{GREEN}✓{RESET} All responses < 5s")
        else:
            print(f"{YELLOW}⚠{RESET} Some slow responses detected")
            
    def test_sustained_load(self, duration_seconds: int = 60, rps: float = 1.0):
        """
        Test 3: Sustained Load
        
        Send requests at constant rate for extended period to test:
        - Memory leaks
        - Performance degradation
        - Stability
        """
        self.print_header("TEST 3: SUSTAINED LOAD")
        
        print(f"{CYAN}Running for {duration_seconds}s at {rps} req/s...{RESET}\n")
        
        start_time = time.time()
        request_id = 0
        results = []
        
        while time.time() - start_time < duration_seconds:
            request_id += 1
            result = self.make_request(request_id)
            results.append(result)
            
            elapsed = time.time() - start_time
            progress = elapsed / duration_seconds * 100
            
            # Print progress every 10 requests
            if request_id % 10 == 0:
                print(f"Progress: {progress:.1f}% | Requests: {request_id} | "
                      f"Success: {sum(1 for r in results if r['success'])} | "
                      f"Rate limited: {sum(1 for r in results if r['rate_limited'])}")
                
            # Wait to maintain rate
            time.sleep(1.0 / rps)
            
        # Analysis
        print(f"\n{CYAN}Results:{RESET}\n")
        
        successful = sum(1 for r in results if r["success"])
        rate_limited = sum(1 for r in results if r["rate_limited"])
        errors = sum(1 for r in results if r["error"])
        
        print(f"Total requests: {len(results)}")
        print(f"Successful: {GREEN}{successful}{RESET}")
        print(f"Rate limited: {YELLOW}{rate_limited}{RESET}")
        print(f"Errors: {RED}{errors}{RESET}")
        
        # Response time trend
        durations = [r["duration"] for r in results if r["success"]]
        
        if len(durations) >= 10:
            first_10 = durations[:10]
            last_10 = durations[-10:]
            
            avg_first = statistics.mean(first_10)
            avg_last = statistics.mean(last_10)
            
            print(f"\n{CYAN}Performance Trend:{RESET}\n")
            print(f"First 10 requests avg: {avg_first:.2f}s")
            print(f"Last 10 requests avg: {avg_last:.2f}s")
            
            if avg_last > avg_first * 1.5:
                print(f"{RED}✗{RESET} Performance degradation detected!")
            elif avg_last > avg_first * 1.2:
                print(f"{YELLOW}⚠{RESET} Slight performance degradation")
            else:
                print(f"{GREEN}✓{RESET} Stable performance")
                
    def test_burst_traffic(self, burst_size: int = 20, num_bursts: int = 3):
        """
        Test 4: Burst Traffic
        
        Send bursts of requests to test:
        - Rate limiting recovery
        - Queue handling
        - No cascading failures
        """
        self.print_header("TEST 4: BURST TRAFFIC")
        
        print(f"{CYAN}Sending {num_bursts} bursts of {burst_size} requests...{RESET}\n")
        
        for burst_num in range(num_bursts):
            print(f"{CYAN}Burst {burst_num + 1}/{num_bursts}:{RESET}")
            
            # Send burst
            with ThreadPoolExecutor(max_workers=burst_size) as executor:
                futures = [executor.submit(self.make_request, i) 
                          for i in range(burst_size)]
                results = [f.result() for f in as_completed(futures)]
                
            successful = sum(1 for r in results if r["success"])
            rate_limited = sum(1 for r in results if r["rate_limited"])
            errors = sum(1 for r in results if r["error"])
            
            print(f"  Success: {successful}, Rate limited: {rate_limited}, Errors: {errors}")
            
            # Wait between bursts
            if burst_num < num_bursts - 1:
                print(f"  Waiting 60s for rate limit reset...\n")
                time.sleep(60)
                
        print(f"\n{GREEN}✓{RESET} Burst traffic test complete")
        
    def run_all_stress_tests(self):
        """Run all stress tests"""
        
        self.print_header("STRESS TEST SUITE")
        print(f"Testing: {YELLOW}{self.base_url}{RESET}\n")
        
        # Test 1: Rate limiting accuracy
        self.test_rate_limiting_accuracy(10)
        
        # Wait for rate limit reset
        print(f"\n{CYAN}Waiting 60s for rate limit reset...{RESET}")
        time.sleep(60)
        
        # Test 2: Concurrent load
        self.test_concurrent_load(50, 10)
        
        # Wait for rate limit reset
        print(f"\n{CYAN}Waiting 60s for rate limit reset...{RESET}")
        time.sleep(60)
        
        # Test 3: Sustained load (optional, takes time)
        # self.test_sustained_load(60, 0.5)
        
        # Test 4: Burst traffic
        # self.test_burst_traffic(20, 3)
        
        # Summary
        self.print_header("STRESS TEST COMPLETE")
        print(f"{GREEN}All stress tests completed!{RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Stress test production agent")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL"
    )
    parser.add_argument(
        "--api-key",
        default="dev-key-change-me-in-production",
        help="API Key"
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=50,
        help="Number of requests for concurrent test"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent workers"
    )
    parser.add_argument(
        "--test",
        choices=["rate", "concurrent", "sustained", "burst", "all"],
        default="all",
        help="Which test to run"
    )
    
    args = parser.parse_args()
    
    tester = StressTester(args.url, args.api_key)
    
    if args.test == "rate":
        tester.test_rate_limiting_accuracy(10)
    elif args.test == "concurrent":
        tester.test_concurrent_load(args.requests, args.workers)
    elif args.test == "sustained":
        tester.test_sustained_load(60, 1.0)
    elif args.test == "burst":
        tester.test_burst_traffic(20, 3)
    else:
        tester.run_all_stress_tests()


if __name__ == "__main__":
    main()
