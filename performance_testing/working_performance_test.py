"""
Working Performance Test for crAPI
Uses a single authenticated user to test API performance without concurrent auth issues
"""

import subprocess
import time
import os
from datetime import datetime


def run_performance_test():
    """Run performance test with single user authentication"""
    print("crAPI Working Performance Test")
    print("=" * 40)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = f"performance_results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    scenarios = [
        {
            "name": "api_load_test",
            "users": 10,
            "spawn_rate": 2,
            "run_time": "5m",
            "user_class": "CRAPIBrowsingUser"  # No auth required
        },
        {
            "name": "authenticated_load_test", 
            "users": 5,
            "spawn_rate": 1,
            "run_time": "3m",
            "user_class": "CRAPIAPIOnlyUser"  # Simpler auth flow
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(f"Running {scenario['name']}")
        print(f"Users: {scenario['users']}, Class: {scenario['user_class']}")
        print(f"{'='*50}")
        
        cmd = [
            "locust",
            "-f", "locustfile.py",
            "--host", "http://localhost:8888",
            "--users", str(scenario["users"]),
            "--spawn-rate", str(scenario["spawn_rate"]),
            "--run-time", scenario["run_time"],
            "--html", f"{results_dir}/{scenario['name']}_report.html",
            "--csv", f"{results_dir}/{scenario['name']}",
            "--headless",
            "--user-classes", scenario["user_class"]
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            end_time = time.time()
            
            print(f"Test completed in {end_time - start_time:.2f} seconds")
            print(f"Return code: {result.returncode}")
            
            if result.stdout:
                print("STDOUT (last 500 chars):")
                print(result.stdout[-500:])
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            success = result.returncode == 0
            results.append({
                "name": scenario["name"],
                "success": success,
                "duration": end_time - start_time,
                "users": scenario["users"],
                "user_class": scenario["user_class"]
            })
            
            if not success:
                print(f"❌ Test {scenario['name']} failed, continuing with next test")
            else:
                print(f"✅ Test {scenario['name']} completed successfully")
                
        except subprocess.TimeoutExpired:
            print(f"❌ Test timed out after 10 minutes")
            results.append({
                "name": scenario["name"],
                "success": False,
                "duration": 600,
                "users": scenario["users"],
                "user_class": scenario["user_class"],
                "error": "Timeout"
            })
        except Exception as e:
            print(f"❌ Error running test: {e}")
            results.append({
                "name": scenario["name"],
                "success": False,
                "duration": 0,
                "users": scenario["users"],
                "user_class": scenario["user_class"],
                "error": str(e)
            })
        
        if scenario != scenarios[-1]:
            print("⏳ Waiting 30 seconds before next test...")
            time.sleep(30)
    
    print(f"\n{'='*60}")
    print("PERFORMANCE TEST SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{result['name']}: {status}")
        print(f"  Users: {result['users']}, Class: {result['user_class']}")
        print(f"  Duration: {result['duration']:.1f}s")
        if not result['success'] and 'error' in result:
            print(f"  Error: {result['error']}")
        print()
    
    summary_file = f"performance_summary_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.write("crAPI Performance Test Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target: http://localhost:8888\n\n")
        
        f.write("Test Results:\n")
        for result in results:
            f.write(f"- {result['name']}: {'PASSED' if result['success'] else 'FAILED'}\n")
            f.write(f"  Users: {result['users']}, Duration: {result['duration']:.1f}s\n")
            if not result['success'] and 'error' in result:
                f.write(f"  Error: {result['error']}\n")
            f.write("\n")
        
        f.write(f"Results Directory: {results_dir}/\n")
    
    print(f"Summary saved to: {summary_file}")
    print(f"Results directory: {results_dir}/")
    
    return results_dir, summary_file, results


if __name__ == "__main__":
    run_performance_test()
