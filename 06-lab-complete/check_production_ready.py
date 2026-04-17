#!/usr/bin/env python3
"""
Production Readiness Checker

Script này kiểm tra xem AI Agent có đáp ứng tất cả yêu cầu production không.

Usage:
    python check_production_ready.py
    python check_production_ready.py --url https://your-app.com
"""
import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class ProductionChecker:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def print_header(self, text: str):
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{text:^60}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
    def print_check(self, name: str, passed: bool, message: str = ""):
        icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"{icon} {name:.<50} {status}")
        if message:
            print(f"  {YELLOW}→ {message}{RESET}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
    def print_warning(self, message: str):
        print(f"{YELLOW}⚠ WARNING: {message}{RESET}")
        self.warnings += 1
        
    def check_file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        return Path(filepath).exists()
        
    def check_dockerfile(self) -> Tuple[bool, str]:
        """Check Dockerfile exists and uses multi-stage build"""
        if not self.check_file_exists("Dockerfile"):
            return False, "Dockerfile not found"
            
        with open("Dockerfile", "r") as f:
            content = f.read()
            
        # Check multi-stage
        if "AS builder" not in content and "AS runtime" not in content:
            return False, "Not using multi-stage build"
            
        # Check non-root user
        if "USER agent" not in content and "USER " not in content:
            return False, "Not using non-root user"
            
        return True, "Multi-stage build with non-root user"
        
    def check_dockerignore(self) -> Tuple[bool, str]:
        """Check .dockerignore exists"""
        if not self.check_file_exists(".dockerignore"):
            return False, ".dockerignore not found"
            
        with open(".dockerignore", "r") as f:
            content = f.read()
            
        required = [".env", "venv", ".git"]
        missing = [item for item in required if item not in content]
        
        if missing:
            return False, f"Missing: {', '.join(missing)}"
            
        return True, "Properly configured"
        
    def check_env_example(self) -> Tuple[bool, str]:
        """Check .env.example has required variables"""
        if not self.check_file_exists(".env.example"):
            return False, ".env.example not found"
            
        with open(".env.example", "r") as f:
            content = f.read()
            
        required = [
            "AGENT_API_KEY",
            "PORT",
            "ENVIRONMENT",
            "REDIS_URL",
            "RATE_LIMIT_PER_MINUTE"
        ]
        
        missing = [var for var in required if var not in content]
        
        if missing:
            return False, f"Missing variables: {', '.join(missing)}"
            
        return True, "All required variables present"
        
    def check_docker_compose(self) -> Tuple[bool, str]:
        """Check docker-compose.yml exists and has required services"""
        if not self.check_file_exists("docker-compose.yml"):
            return False, "docker-compose.yml not found"
            
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            
        if "agent:" not in content:
            return False, "Missing agent service"
            
        if "redis:" not in content:
            return False, "Missing redis service"
            
        if "healthcheck:" not in content:
            return False, "Missing healthcheck configuration"
            
        return True, "Agent + Redis with healthchecks"
        
    def check_requirements(self) -> Tuple[bool, str]:
        """Check requirements.txt has necessary packages"""
        if not self.check_file_exists("requirements.txt"):
            return False, "requirements.txt not found"
            
        with open("requirements.txt", "r") as f:
            content = f.read()
            
        required = ["fastapi", "uvicorn", "redis", "pydantic"]
        missing = [pkg for pkg in required if pkg not in content.lower()]
        
        if missing:
            return False, f"Missing packages: {', '.join(missing)}"
            
        return True, "All required packages present"
        
    def check_endpoint(self, path: str, expected_status: int = 200) -> Tuple[bool, str]:
        """Check if endpoint returns expected status"""
        try:
            import urllib.request
            import urllib.error
            
            url = f"{self.base_url}{path}"
            req = urllib.request.Request(url)
            
            try:
                response = urllib.request.urlopen(req, timeout=5)
                status = response.getcode()
                
                if status == expected_status:
                    return True, f"Returns {status}"
                else:
                    return False, f"Expected {expected_status}, got {status}"
                    
            except urllib.error.HTTPError as e:
                if e.code == expected_status:
                    return True, f"Returns {e.code}"
                return False, f"Expected {expected_status}, got {e.code}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def check_auth_required(self) -> Tuple[bool, str]:
        """Check if /ask requires authentication"""
        try:
            import urllib.request
            import urllib.error
            
            url = f"{self.base_url}/ask"
            data = json.dumps({"question": "test"}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            
            try:
                urllib.request.urlopen(req, timeout=5)
                return False, "Endpoint accessible without API key"
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    return True, "Returns 401 Unauthorized"
                return False, f"Expected 401, got {e.code}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def check_rate_limiting(self, api_key: str = "dev-key-change-me-in-production") -> Tuple[bool, str]:
        """Check if rate limiting works"""
        try:
            import urllib.request
            import urllib.error
            
            url = f"{self.base_url}/ask"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": api_key
            }
            
            # Make 6 requests quickly
            for i in range(6):
                data = json.dumps({"question": f"test {i}"}).encode()
                req = urllib.request.Request(url, data=data, headers=headers)
                
                try:
                    urllib.request.urlopen(req, timeout=5)
                except urllib.error.HTTPError as e:
                    if e.code == 429 and i >= 4:  # Should hit limit around 5th request
                        return True, f"Rate limited after {i+1} requests"
                        
            return False, "No rate limiting detected (made 6 requests)"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def check_docker_image_size(self) -> Tuple[bool, str]:
        """Check Docker image size"""
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Size}}", "06-lab-complete-agent"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, "Image not found (run 'docker compose build' first)"
                
            size_str = result.stdout.strip()
            
            # Parse size (e.g., "450MB" or "1.2GB")
            if "GB" in size_str:
                size_mb = float(size_str.replace("GB", "")) * 1024
            else:
                size_mb = float(size_str.replace("MB", ""))
                
            if size_mb < 500:
                return True, f"Size: {size_str} (< 500 MB)"
            else:
                return False, f"Size: {size_str} (> 500 MB)"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def check_structured_logging(self) -> Tuple[bool, str]:
        """Check if app uses structured JSON logging"""
        if not self.check_file_exists("app/main.py"):
            return False, "app/main.py not found"
            
        with open("app/main.py", "r") as f:
            content = f.read()
            
        if "json.dumps" not in content or "logger" not in content:
            return False, "Not using structured JSON logging"
            
        return True, "Using structured JSON logging"
        
    def check_graceful_shutdown(self) -> Tuple[bool, str]:
        """Check if app handles SIGTERM"""
        if not self.check_file_exists("app/main.py"):
            return False, "app/main.py not found"
            
        with open("app/main.py", "r") as f:
            content = f.read()
            
        if "signal.signal" not in content or "SIGTERM" not in content:
            return False, "Not handling SIGTERM"
            
        return True, "Handles SIGTERM for graceful shutdown"
        
    def run_all_checks(self):
        """Run all production readiness checks"""
        self.print_header("PRODUCTION READINESS CHECKER")
        
        print(f"Checking: {self.base_url}\n")
        
        # File structure checks
        self.print_header("📁 File Structure")
        
        passed, msg = self.check_dockerfile()
        self.print_check("Dockerfile (multi-stage)", passed, msg)
        
        passed, msg = self.check_dockerignore()
        self.print_check(".dockerignore", passed, msg)
        
        passed, msg = self.check_env_example()
        self.print_check(".env.example", passed, msg)
        
        passed, msg = self.check_docker_compose()
        self.print_check("docker-compose.yml", passed, msg)
        
        passed, msg = self.check_requirements()
        self.print_check("requirements.txt", passed, msg)
        
        # Code quality checks
        self.print_header("💻 Code Quality")
        
        passed, msg = self.check_structured_logging()
        self.print_check("Structured logging", passed, msg)
        
        passed, msg = self.check_graceful_shutdown()
        self.print_check("Graceful shutdown", passed, msg)
        
        # Docker checks
        self.print_header("🐳 Docker")
        
        passed, msg = self.check_docker_image_size()
        self.print_check("Image size < 500 MB", passed, msg)
        
        # Runtime checks (only if server is running)
        self.print_header("🚀 Runtime Checks")
        
        print(f"{YELLOW}Note: These checks require the server to be running{RESET}")
        print(f"{YELLOW}Run: docker compose up -d{RESET}\n")
        
        passed, msg = self.check_endpoint("/health", 200)
        self.print_check("Health endpoint (/health)", passed, msg)
        
        passed, msg = self.check_endpoint("/ready", 200)
        self.print_check("Readiness endpoint (/ready)", passed, msg)
        
        passed, msg = self.check_auth_required()
        self.print_check("Authentication required", passed, msg)
        
        passed, msg = self.check_rate_limiting()
        self.print_check("Rate limiting (5 req/min)", passed, msg)
        
        # Summary
        self.print_header("📊 SUMMARY")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"Total checks: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Warnings: {self.warnings}{RESET}")
        print(f"\nScore: {percentage:.1f}%\n")
        
        if percentage >= 90:
            print(f"{GREEN}🎉 EXCELLENT! Production ready!{RESET}")
            return 0
        elif percentage >= 70:
            print(f"{YELLOW}⚠️  GOOD, but needs improvement{RESET}")
            return 1
        else:
            print(f"{RED}❌ NOT READY for production{RESET}")
            return 2


def main():
    parser = argparse.ArgumentParser(description="Check production readiness")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL to check (default: http://localhost:8000)"
    )
    args = parser.parse_args()
    
    checker = ProductionChecker(args.url)
    exit_code = checker.run_all_checks()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
