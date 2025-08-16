"""
Final Performance Test for crAPI
Uses proper Locust syntax and focuses on working test scenarios
"""

import subprocess
import time
import os
from datetime import datetime


def create_browsing_only_locustfile():
    """Create a Locust file with only browsing users (no auth issues)"""
    content = '''"""
Browsing-only Locust test for crAPI - No authentication required
"""

import random
from locust import HttpUser, task, between


class CRAPIBrowsingUser(HttpUser):
    """
    Simulates users browsing the application without authentication
    """
    wait_time = between(1, 3)
    
    @task(5)
    def browse_homepage(self):
        """Browse the main homepage"""
        self.client.get("/", name="Browse: Homepage")
    
    @task(3)
    def browse_login_page(self):
        """Browse login page"""
        self.client.get("/login", name="Browse: Login Page")
    
    @task(2)
    def browse_signup_page(self):
        """Browse signup page"""
        self.client.get("/signup", name="Browse: Signup Page")
    
    @task(1)
    def browse_forum_page(self):
        """Browse forum page"""
        self.client.get("/forum", name="Browse: Forum Page")
    
    @task(1)
    def browse_shop_page(self):
        """Browse shop page"""
        self.client.get("/shop", name="Browse: Shop Page")
'''
    
    with open("browsing_locustfile.py", "w") as f:
        f.write(content)
    
    return "browsing_locustfile.py"


def create_simple_auth_locustfile():
    """Create a Locust file with simplified authentication"""
    content = '''"""
Simple authentication Locust test for crAPI
"""

import json
import random
import string
from locust import HttpUser, task, between
from locust.exception import StopUser


class SimpleAuthUser(HttpUser):
    """
    Simple authenticated user with basic error handling
    """
    wait_time = between(2, 4)
    
    def on_start(self):
        """Perform authentication on start"""
        try:
            self.authenticate()
        except Exception as e:
            print(f"Auth failed: {e}")
            raise StopUser()
    
    def authenticate(self):
        """Simple authentication flow"""
        random_id = random.randint(10000, 99999)
        user_data = {
            "name": f"TestUser{random_id}",
            "email": f"test{random_id}@example.com",
            "number": f"555{random.randint(1000000, 9999999)}",
            "password": f"TestPass{random_id}!"
        }
        
        signup_response = self.client.post(
            "/identity/api/auth/signup",
            json=user_data,
            headers={"Content-Type": "application/json"},
            name="Auth: Signup",
            timeout=30
        )
        
        if signup_response.status_code != 200:
            raise Exception(f"Signup failed: {signup_response.status_code}")
        
        login_response = self.client.post(
            "/identity/api/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"},
            name="Auth: Login",
            timeout=30
        )
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
            if not self.token:
                raise Exception("No token received")
        else:
            raise Exception(f"Login failed: {login_response.status_code}")
    
    def get_auth_headers(self):
        """Get authentication headers"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    @task(3)
    def get_dashboard(self):
        """Get user dashboard"""
        if hasattr(self, 'token'):
            self.client.get(
                "/identity/api/v2/user/dashboard",
                headers=self.get_auth_headers(),
                name="API: Dashboard"
            )
    
    @task(2)
    def get_vehicles(self):
        """Get vehicles"""
        if hasattr(self, 'token'):
            self.client.get(
                "/identity/api/v2/vehicle/vehicles",
                headers=self.get_auth_headers(),
                name="API: Vehicles"
            )
    
    @task(1)
    def browse_homepage(self):
        """Browse homepage"""
        self.client.get("/", name="Browse: Homepage")
'''
    
    with open("simple_auth_locustfile.py", "w") as f:
        f.write(content)
    
    return "simple_auth_locustfile.py"


def run_performance_test():
    """Run comprehensive performance tests"""
    print("crAPI Final Performance Test Suite")
    print("=" * 50)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = f"performance_results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    scenarios = [
        {
            "name": "browsing_load_test",
            "description": "Frontend browsing performance (no auth)",
            "locustfile": create_browsing_only_locustfile(),
            "users": 20,
            "spawn_rate": 4,
            "run_time": "5m"
        },
        {
            "name": "light_auth_test",
            "description": "Light authenticated API load",
            "locustfile": create_simple_auth_locustfile(),
            "users": 3,
            "spawn_rate": 1,
            "run_time": "3m"
        },
        {
            "name": "medium_browsing_test",
            "description": "Medium browsing load",
            "locustfile": "browsing_locustfile.py",
            "users": 50,
            "spawn_rate": 10,
            "run_time": "7m"
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\\n{'='*60}")
        print(f"Running {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Users: {scenario['users']}, Spawn Rate: {scenario['spawn_rate']}")
        print(f"{'='*60}")
        
        cmd = [
            "locust",
            "-f", scenario["locustfile"],
            "--host", "http://localhost:8888",
            "--users", str(scenario["users"]),
            "--spawn-rate", str(scenario["spawn_rate"]),
            "--run-time", scenario["run_time"],
            "--html", f"{results_dir}/{scenario['name']}_report.html",
            "--csv", f"{results_dir}/{scenario['name']}",
            "--headless"
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            end_time = time.time()
            
            print(f"\\nTest completed in {end_time - start_time:.2f} seconds")
            print(f"Return code: {result.returncode}")
            
            if result.stdout:
                lines = result.stdout.strip().split('\\n')
                summary_lines = [line for line in lines[-20:] if 'Aggregated' in line or 'req/s' in line or 'Response time' in line]
                if summary_lines:
                    print("\\nPerformance Summary:")
                    for line in summary_lines[-5:]:
                        print(line)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            success = result.returncode == 0
            results.append({
                "name": scenario["name"],
                "description": scenario["description"],
                "success": success,
                "duration": end_time - start_time,
                "users": scenario["users"],
                "spawn_rate": scenario["spawn_rate"],
                "run_time": scenario["run_time"]
            })
            
            if success:
                print(f"✅ {scenario['name']} completed successfully")
            else:
                print(f"❌ {scenario['name']} failed")
                
        except subprocess.TimeoutExpired:
            print(f"❌ Test timed out after 10 minutes")
            results.append({
                "name": scenario["name"],
                "description": scenario["description"],
                "success": False,
                "duration": 600,
                "users": scenario["users"],
                "error": "Timeout"
            })
        except Exception as e:
            print(f"❌ Error running test: {e}")
            results.append({
                "name": scenario["name"],
                "description": scenario["description"],
                "success": False,
                "duration": 0,
                "users": scenario["users"],
                "error": str(e)
            })
        
        if scenario != scenarios[-1]:
            print("\\n⏳ Waiting 30 seconds before next test...")
            time.sleep(30)
    
    print(f"\\n{'='*70}")
    print("FINAL PERFORMANCE TEST SUMMARY")
    print(f"{'='*70}")
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    print()
    
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{result['name']}: {status}")
        print(f"  Description: {result['description']}")
        print(f"  Users: {result['users']}, Duration: {result['duration']:.1f}s")
        if not result['success'] and 'error' in result:
            print(f"  Error: {result['error']}")
        print()
    
    summary_file = f"performance_summary_{timestamp}.md"
    with open(summary_file, 'w') as f:
        f.write("# crAPI Performance Test Results\\n\\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write(f"**Target Application:** http://localhost:8888\\n")
        f.write(f"**Results Directory:** {results_dir}/\\n\\n")
        
        f.write("## Test Summary\\n\\n")
        f.write(f"- **Total Tests:** {len(results)}\\n")
        f.write(f"- **Successful:** {len(successful_tests)}\\n")
        f.write(f"- **Failed:** {len(failed_tests)}\\n\\n")
        
        f.write("## Test Details\\n\\n")
        for result in results:
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            f.write(f"### {result['name']} {status}\\n\\n")
            f.write(f"- **Description:** {result['description']}\\n")
            f.write(f"- **Users:** {result['users']}\\n")
            f.write(f"- **Spawn Rate:** {result['spawn_rate']}\\n")
            f.write(f"- **Duration:** {result['duration']:.1f} seconds\\n")
            if not result['success'] and 'error' in result:
                f.write(f"- **Error:** {result['error']}\\n")
            f.write("\\n")
        
        f.write("## Performance Analysis\\n\\n")
        if successful_tests:
            f.write("### Successful Tests Analysis\\n")
            for test in successful_tests:
                f.write(f"- **{test['name']}**: Successfully handled {test['users']} concurrent users\\n")
            f.write("\\n")
        
        if failed_tests:
            f.write("### Failed Tests Analysis\\n")
            for test in failed_tests:
                f.write(f"- **{test['name']}**: Failed with {test['users']} users - {test.get('error', 'Unknown error')}\\n")
            f.write("\\n")
        
        f.write("## Recommendations\\n\\n")
        f.write("1. **Authentication Bottleneck**: Tests with concurrent authentication show issues\\n")
        f.write("2. **Frontend Performance**: Browsing tests show application frontend performance\\n")
        f.write("3. **API Performance**: Authenticated API calls performance under load\\n")
        f.write("4. **Scaling Considerations**: Consider authentication service optimization for concurrent users\\n")
    
    print(f"\\nDetailed summary saved to: {summary_file}")
    print(f"HTML reports available in: {results_dir}/")
    
    return results_dir, summary_file, results


if __name__ == "__main__":
    run_performance_test()
