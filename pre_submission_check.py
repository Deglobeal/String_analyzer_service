import requests
import hashlib

BASE_URL = "http://localhost:8000"

def quick_check():
    """Quick check of the most critical endpoints"""
    print("🚀 PRE-SUBMISSION QUICK CHECK")
    print("=" * 50)
    
    checks = []
    
    # 1. POST /strings
    test_str = "quick_test"
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_str})
    checks.append(("POST /strings (new)", response.status_code == 201))
    
    # 2. POST /strings (duplicate)
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_str})
    checks.append(("POST /strings (duplicate)", response.status_code == 409))
    
    # 3. GET /strings/{value}
    response = requests.get(f"{BASE_URL}/strings/{test_str}")
    checks.append(("GET /strings/{value}", response.status_code == 200))
    
    # 4. GET /strings?filters
    response = requests.get(f"{BASE_URL}/strings?is_palindrome=true")
    checks.append(("GET /strings?filters", response.status_code == 200))
    
    # 5. GET /strings/filter-by-natural-language
    response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query=test")
    checks.append(("GET /natural-language", response.status_code == 200))
    
    # 6. DELETE /strings/{value}
    response = requests.delete(f"{BASE_URL}/strings/{test_str}")
    checks.append(("DELETE /strings/{value}", response.status_code == 204))
    
    # 7. Verify SHA-256
    response = requests.post(f"{BASE_URL}/strings", json={"value": "sha_test"})
    if response.status_code == 201:
        data = response.json()
        expected = hashlib.sha256("sha_test".encode()).hexdigest()
        actual = data.get('properties', {}).get('sha256_hash')
        checks.append(("SHA-256 calculation", actual == expected))
    
    # Results
    print("\n📋 CHECK RESULTS:")
    passed = 0
    for check_name, success in checks:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {check_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 SCORE: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("🚀 READY FOR SUBMISSION! All critical checks passed.")
    else:
        print("⚠️  NOT READY! Fix the failed checks before submission.")

if __name__ == "__main__":
    quick_check()