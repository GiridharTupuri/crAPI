"""
Targeted Performance Test for crAPI
Runs specific load scenarios with better error handling
"""

import subprocess
import time
import os
from datetime import datetime


def run_single_test(users, spawn_rate, run_time, test_name):
    """Run a single targeted performance test"""
    print(f"\n{'='*50}")
    print(f"Running {test_name}")
    print(f"Users: {users}, Spawn Rate: {spawn_rate}, Duration: {run_time}")
    print(f"{'='*50}")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = f"performance_results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--host", "http://localhost:8888",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--html", f"{results_dir}/{test_name}_report.html",
        "--csv", f"{results_dir}/{test_name}",
        "--headless",
        "--logfile", f"{results_dir}/{test_name}_log.txt"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)  # 15 min timeout
        end_time = time.time()
        
        print(f"Test completed in {end_time - start_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT (last 1000 chars):")
            print(result.stdout[-1000:])
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return {
            "test_name": test_name,
            "success": result.returncode == 0,
            "duration": end_time - start_time,
            "results_dir": results_dir,
            "users": users,
            "spawn_rate": spawn_rate,
            "run_time": run_time
        }
        
    except subprocess.TimeoutExpired:
        print(f"Test timed out after 15 minutes")
        return {
            "test_name": test_name,
            "success": False,
            "duration": 900,
            "results_dir": results_dir,
            "error": "Timeout",
            "users": users,
            "spawn_rate": spawn_rate,
            "run_time": run_time
        }
    except Exception as e:
        print(f"Error running test: {e}")
        return {
            "test_name": test_name,
            "success": False,
            "duration": 0,
            "results_dir": results_dir,
            "error": str(e),
            "users": users,
            "spawn_rate": spawn_rate,
            "run_time": run_time
        }


def main():
    """Run targeted performance tests"""
    print("crAPI Targeted Performance Testing")
    print("=" * 40)
    
    test_scenarios = [
        {"users": 5, "spawn_rate": 1, "run_time": "3m", "name": "baseline_5_users"},
        {"users": 10, "spawn_rate": 2, "run_time": "5m", "name": "light_load_10_users"},
        {"users": 25, "spawn_rate": 3, "run_time": "7m", "name": "medium_load_25_users"},
        {"users": 50, "spawn_rate": 5, "run_time": "10m", "name": "heavy_load_50_users"}
    ]
    
    results = []
    
    for scenario in test_scenarios:
        result = run_single_test(
            scenario["users"],
            scenario["spawn_rate"], 
            scenario["run_time"],
            scenario["name"]
        )
        results.append(result)
        
        if not result["success"]:
            print(f"\n❌ Test {scenario['name']} failed, stopping test suite")
            break
        
        print(f"\n⏳ Waiting 30 seconds before next test...")
        time.sleep(30)
    
    print(f"\n{'='*60}")
    print("PERFORMANCE TEST SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{result['test_name']}: {status}")
        print(f"  Users: {result['users']}, Duration: {result['duration']:.1f}s")
        if result['success']:
            print(f"  Results: {result['results_dir']}/")
        else:
            print(f"  Error: {result.get('error', 'Unknown')}")
        print()
    
    summary_file = f"performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w') as f:
        f.write("crAPI Performance Test Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in results:
            f.write(f"Test: {result['test_name']}\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Users: {result['users']}\n")
            f.write(f"Duration: {result['duration']:.2f} seconds\n")
            if result['success']:
                f.write(f"Results: {result['results_dir']}/\n")
            f.write("\n")
    
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()
