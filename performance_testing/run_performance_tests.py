"""
Performance Test Runner for crAPI
Executes different load testing scenarios and generates reports
"""

import subprocess
import time
import json
import os
from datetime import datetime
from locust_config import TEST_SCENARIOS, PERFORMANCE_THRESHOLDS


def run_locust_test(scenario_name, scenario_config, host="http://localhost:8888"):
    """Run a single Locust test scenario"""
    print(f"\n{'='*60}")
    print(f"Running {scenario_name}: {scenario_config['description']}")
    print(f"{'='*60}")
    
    results_dir = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(results_dir, exist_ok=True)
    
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--host", host,
        "--users", str(scenario_config["users"]),
        "--spawn-rate", str(scenario_config["spawn_rate"]),
        "--run-time", scenario_config["run_time"],
        "--html", f"{results_dir}/{scenario_name}_report.html",
        "--csv", f"{results_dir}/{scenario_name}",
        "--headless"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Results will be saved to: {results_dir}/")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
        end_time = time.time()
        
        print(f"\nTest completed in {end_time - start_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return {
            "scenario": scenario_name,
            "success": result.returncode == 0,
            "duration": end_time - start_time,
            "results_dir": results_dir,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"Test timed out after 30 minutes")
        return {
            "scenario": scenario_name,
            "success": False,
            "duration": 1800,
            "results_dir": results_dir,
            "error": "Timeout"
        }
    except Exception as e:
        print(f"Error running test: {e}")
        return {
            "scenario": scenario_name,
            "success": False,
            "duration": 0,
            "results_dir": results_dir,
            "error": str(e)
        }


def analyze_results(test_results):
    """Analyze test results and generate summary"""
    print(f"\n{'='*60}")
    print("PERFORMANCE TEST SUMMARY")
    print(f"{'='*60}")
    
    for result in test_results:
        print(f"\nScenario: {result['scenario']}")
        print(f"Success: {result['success']}")
        print(f"Duration: {result['duration']:.2f} seconds")
        
        if result['success']:
            print(f"Results directory: {result['results_dir']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    summary_file = f"performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w') as f:
        f.write("crAPI Performance Test Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target Application: http://localhost:8888\n\n")
        
        for result in test_results:
            f.write(f"Scenario: {result['scenario']}\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Duration: {result['duration']:.2f} seconds\n")
            if result['success']:
                f.write(f"Results: {result['results_dir']}/\n")
            f.write("\n")
    
    print(f"\nSummary saved to: {summary_file}")
    return summary_file


def main():
    """Main function to run all performance tests"""
    print("crAPI Performance Testing Suite")
    print("=" * 40)
    
    try:
        result = subprocess.run(["locust", "--version"], capture_output=True, text=True)
        print(f"Locust version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("ERROR: Locust not found. Please install Locust first.")
        return
    
    try:
        import requests
        response = requests.get("http://localhost:8888", timeout=10)
        print(f"crAPI status: HTTP {response.status_code}")
    except Exception as e:
        print(f"ERROR: Cannot connect to crAPI at localhost:8888: {e}")
        return
    
    test_results = []
    
    for scenario_name, scenario_config in TEST_SCENARIOS.items():
        result = run_locust_test(scenario_name, scenario_config)
        test_results.append(result)
        
        if scenario_name != list(TEST_SCENARIOS.keys())[-1]:  # Not the last test
            print(f"\nWaiting 30 seconds before next test...")
            time.sleep(30)
    
    summary_file = analyze_results(test_results)
    
    print(f"\n{'='*60}")
    print("ALL PERFORMANCE TESTS COMPLETED")
    print(f"Summary report: {summary_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
