#!/usr/bin/env python3
import sys
import os
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test(test_file):
    print(f"Running {test_file}...")
    result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {test_file} passed")
        return True
    else:
        print(f"❌ {test_file} failed")
        print(result.stdout)
        print(result.stderr)
        return False

def main():
    test_files = [
        'test_producer.py'
    ]
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if run_test(test_file):
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main() 