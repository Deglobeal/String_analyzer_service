import requests
import hashlib

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def quick_railway_test():
    """Quick test to verify Railway deployment is working"""
    print("🚀 QUICK RAILWAY DEPLOYMENT TEST")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(BASE_URL, timeout=10)
        tests.append(("Basic Connectivity", response.status_code == 200))
    except:
        tests.append(("Basic Connectivity", False))
    
    # Test 2: POST /strings
    try:
        test_str = f"railway_test"
        response = requests.post(f"{BASE_URL}/strings", json={"value": test_str}, timeout=10)
        tests.append(("POST /strings", response.status_code == 201))
        
        if response.status_code == 201:
            # Test SHA-256
            data = response.json()
            expected_hash = hashlib.sha256(test_str.encode()).hexdigest()
            tests.append(("SHA-256 Hash", data.get('properties', {}).get('sha256_hash') == expected_hash))
    except:
        tests.append(("POST /strings", False))
        tests.append(("SHA-256 Hash", False))
    
    # Test 3: GET /strings with filters
    try:
        response = requests.get(f"{BASE_URL}/strings?is_palindrome=true", timeout=10)
        tests.append(("GET with filters", response.status_code == 200))
    except:
        tests.append(("GET with filters", False))
    
    # Test 4: Natural language filter
    try:
        response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query=test", timeout=10)
        tests.append(("Natural Language", response.status_code == 200))
    except:
        tests.append(("Natural Language", False))
    
    # Test 5: DELETE
    try:
        response = requests.delete(f"{BASE_URL}/strings/railway_test", timeout=10)
        tests.append(("DELETE", response.status_code in [204, 404]))
    except:
        tests.append(("DELETE", False))
    
    # Results
    print("\n📋 TEST RESULTS:")
    passed = 0
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 SCORE: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🚀 EXCELLENT! Railway deployment is working correctly.")
        print("   Run the full bot test to verify complete compatibility.")
    else:
        print("⚠️  Some tests failed. Check your Railway deployment.")
        print("   Common issues:")
        print("   - CORS configuration")
        print("   - URL routing")
        print("   - Database connectivity")

if __name__ == "__main__":
    quick_railway_test()