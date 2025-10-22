# corrected_test.py
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def run_corrected_tests():
    print("=== CORRECTED TESTS ===")
    total_score = 0
    
    # Test POST /strings
    print("\n1. Testing POST /strings")
    unique_str = f"test_{uuid.uuid4().hex[:8]}"
    response = requests.post(f"{BASE_URL}/strings", json={"value": unique_str})
    if response.status_code == 201:
        print("✓ POST /strings: Success")
        total_score += 25
    else:
        print(f"✗ POST /strings: Failed with status {response.status_code}")
    
    # Test GET specific string
    print("\n2. Testing GET /strings/{value}")
    response = requests.get(f"{BASE_URL}/strings/{unique_str}")
    if response.status_code == 200:
        print("✓ GET specific string: Success")
        total_score += 15
    else:
        print(f"✗ GET specific string: Failed with status {response.status_code}")
    
    # Test GET /strings with filters
    print("\n3. Testing GET /strings with filters")
    response = requests.get(f"{BASE_URL}/strings?is_palindrome=true")
    if response.status_code == 200:
        print("✓ GET with filters: Success")
        total_score += 25
    else:
        print(f"✗ GET with filters: Failed with status {response.status_code}")
    
    # Test Natural Language Filter
    print("\n4. Testing Natural Language Filter")
    response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query=palindromic strings")
    if response.status_code == 200:
        print("✓ Natural Language Filter: Success")
        total_score += 20
    else:
        print(f"✗ Natural Language Filter: Failed with status {response.status_code}")
        print("  This suggests the URL routing is incorrect")
    
    # Test DELETE
    print("\n5. Testing DELETE /strings/{value}")
    response = requests.delete(f"{BASE_URL}/strings/{unique_str}")
    if response.status_code == 204:
        print("✓ DELETE string: Success")
        total_score += 15
    else:
        print(f"✗ DELETE string: Failed with status {response.status_code}")
    
    print(f"\n=== FINAL SCORE: {total_score}/100 ===")
    
    # Debug: Check all available endpoints
    print("\n=== DEBUG: Testing all endpoints ===")
    endpoints = [
        "/strings",
        "/strings/filter-by-natural-language?query=test",
    ]
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        try:
            if endpoint == "/strings":
                response = requests.get(url)
            else:
                response = requests.get(url)
            print(f"GET {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint}: {e}")

if __name__ == "__main__":
    run_corrected_tests()