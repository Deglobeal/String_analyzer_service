import requests
import hashlib
import uuid
import json

BASE_URL = "http://localhost:8000"

def run_bot_tests():
    """
    EXACT replica of the bot's test format and requirements
    """
    print("=" * 60)
    print("=" * 60)
    
    total_score = 0
    
    # === POST /strings (25 points) ===
    print("=== POST /strings (25 points) ===")
    post_score = 0
    
    # Test 1: Successful creation (5 points)
    test_string = f"test_string_{uuid.uuid4().hex[:8]}"
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    if response.status_code == 201:
        data = response.json()
        # Verify SHA256 hash calculation
        expected_hash = hashlib.sha256(test_string.encode()).hexdigest()
        if (data.get('properties', {}).get('sha256_hash') == expected_hash and
            data.get('value') == test_string and
            'id' in data and 'properties' in data and 'created_at' in data):
            post_score += 5
            print("✓ status code:  (expected 201) (5/5 pts)")
        else:
            print(f"✗ Wrong status code: 201 but data incorrect (0/5 pts)")
    else:
        print(f"✗ Wrong status code: {response.status_code} (expected 201) (0/5 pts)")

    # Test 2: Duplicate string (5 points)
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    if response.status_code == 409:
        post_score += 5
        print("✓ status for duplicate:  (expected 409) (5/5 pts)")
    else:
        print(f"✗ Wrong status for duplicate: {response.status_code} (expected 409) (0/5 pts)")

    # Test 3: Missing value field (2 points)
    response = requests.post(f"{BASE_URL}/strings", json={"wrong_field": "test"})
    if response.status_code == 400:
        post_score += 2
        print("✓ status for missing 'value' field: 405 (2/2 pts)")
    else:
        print(f"✗ Wrong status for missing 'value' field: {response.status_code} (0/2 pts)")

    # Test 4: Invalid data type (3 points)
    response = requests.post(f"{BASE_URL}/strings", json={"value": 123})
    if response.status_code == 422:
        post_score += 3
        print("✓ status for invalid data type: 405 (3/3 pts)")
    else:
        print(f"✗ Wrong status for invalid data type: {response.status_code} (0/3 pts)")

    print(f"POST /strings score: {post_score}/25")
    total_score += post_score

    # === GET /strings/{string_value} (15 points) ===
    print("\n=== GET /strings/{string_value} (15 points) ===")
    get_specific_score = 0
    
    # Test: Non-existent string (5 points)
    response = requests.get(f"{BASE_URL}/strings/nonexistent_string_12345")
    if response.status_code == 404:
        get_specific_score += 5
        print("✓ Returns 404 for non-existent string (5/5 pts)")
    else:
        print(f"✗ Returns {response.status_code} for non-existent string (expected 404) (0/5 pts)")

    # Test: Existing string (10 points)
    response = requests.get(f"{BASE_URL}/strings/{test_string}")
    if response.status_code == 200:
        data = response.json()
        if (data.get('value') == test_string and 
            'properties' in data and 
            'id' in data and 
            'created_at' in data):
            get_specific_score += 10
            print("✓ Returns 200 with correct data for existing string (10/10 pts)")
        else:
            print("✗ Returns 200 but with incorrect/missing data (0/10 pts)")
    else:
        print(f"✗ Returns {response.status_code} for existing string (expected 200) (0/10 pts)")

    print(f"GET specific string score: {get_specific_score}/15")
    total_score += get_specific_score

    # === GET /strings with filters (25 points) ===
    print("\n=== GET /strings with filters (25 points) ===")
    filter_score = 0
    
    # Create test data for filters
    test_strings = [
        f"a_{uuid.uuid4().hex[:4]}",  # palindrome, 1 word
        f"madam_{uuid.uuid4().hex[:4]}",  # palindrome, 1 word
        f"hello world_{uuid.uuid4().hex[:4]}",  # 2 words
        f"python code_{uuid.uuid4().hex[:4]}",  # 2 words, contains 'o'
        f"test example_{uuid.uuid4().hex[:4]}"  # 2 words
    ]
    
    for string in test_strings:
        try:
            requests.post(f"{BASE_URL}/strings", json={"value": string})
        except:
            pass

    # Test each filter (5 points each)
    filter_tests = [
        ("is_palindrome=true", "is_palindrome"),
        ("min_length=5&max_length=15", "length filters"),
        ("word_count=2", "word_count"), 
        ("contains_character=o", "contains_character"),
        ("is_palindrome=true&min_length=3", "combined filters")
    ]
    
    all_filters_working = True
    for filter_query, filter_name in filter_tests:
        response = requests.get(f"{BASE_URL}/strings?{filter_query}")
        if response.status_code == 200:
            data = response.json()
            if ('data' in data and 'filters_applied' in data and 
                'count' in data and isinstance(data['data'], list)):
                filter_score += 5
                print(f"✓ {filter_name} filter works (5/5 pts)")
            else:
                print(f"✗ {filter_name} filter - missing response fields (0/5 pts)")
                all_filters_working = False
        else:
            print(f"✗ {filter_name} filter - status {response.status_code} (0/5 pts)")
            all_filters_working = False

    print(f"GET with filters score: {filter_score}/25")
    total_score += filter_score

    # === GET /strings/filter-by-natural-language (20 points) ===
    print("\n=== GET /strings/filter-by-natural-language (20 points) ===")
    nl_score = 0
    
    # Test natural language queries (5 points each)
    test_queries = [
        "all single word palindromic strings",
        "strings longer than 5 characters", 
        "palindromic strings that contain the letter a",
        "strings containing the letter e"
    ]
    
    for query in test_queries:
        response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}")
        if response.status_code == 200:
            data = response.json()
            if ('data' in data and 'interpreted_query' in data and 
                'count' in data and isinstance(data['data'], list)):
                nl_score += 5
                print(f"✓ Natural language query: '{query}' (5/5 pts)")
            else:
                print(f"✗ Natural language query: '{query}' - missing response fields (0/5 pts)")
        else:
            print(f"✗ Natural language query: '{query}' - status {response.status_code} (0/5 pts)")

    print(f"Natural language filter score: {nl_score}/20")
    total_score += nl_score

    # === DELETE /strings/{string_value} (15 points) ===
    print("\n=== DELETE /strings/{string_value} (15 points) ===")
    delete_score = 0
    
    # Test 1: Delete existing string (10 points)
    delete_test_string = f"delete_test_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/strings", json={"value": delete_test_string})
    
    response = requests.delete(f"{BASE_URL}/strings/{delete_test_string}")
    if response.status_code == 204:
        # Verify it's actually deleted
        get_response = requests.get(f"{BASE_URL}/strings/{delete_test_string}")
        if get_response.status_code == 404:
            delete_score += 10
            print("✓ DELETE existing string (10/10 pts)")
        else:
            print("✗ DELETE returned 204 but string still exists (0/10 pts)")
    else:
        print(f"✗ DELETE existing string - status {response.status_code} (0/10 pts)")

    # Test 2: Delete non-existent string (5 points)
    response = requests.delete(f"{BASE_URL}/strings/nonexistent_delete_test_123")
    if response.status_code == 404:
        delete_score += 5
        print("✓ DELETE non-existent string (5/5 pts)")
    else:
        print(f"✗ DELETE non-existent string - status {response.status_code} (0/5 pts)")

    print(f"DELETE string score: {delete_score}/15")
    total_score += delete_score

    # === Final Results ===
    print("\n=== Cleanup ===")
    print(f"FINAL SCORE: {total_score}/100 ({total_score}%)")
    print("=" * 60)
    
    return total_score

def verify_critical_requirements():
    """
    Verify the specific issues mentioned by the bot
    """
    print("🔍 VERIFYING CRITICAL BOT REQUIREMENTS")
    print("=" * 50)
    
    all_passed = True
    
    # 1. Check SHA-256 hash calculation
    print("\n1. SHA-256 Hash Verification:")
    test_string = "test_sha256"
    expected_hash = hashlib.sha256(test_string.encode()).hexdigest()
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    
    if response.status_code in [201, 409]:  # Created or already exists
        if response.status_code == 201:
            data = response.json()
        else:
            # Get existing string
            get_response = requests.get(f"{BASE_URL}/strings/{test_string}")
            data = get_response.json() if get_response.status_code == 200 else None
        
        if data and data.get('properties', {}).get('sha256_hash') == expected_hash:
            print("   ✅ SHA-256 hash calculated correctly")
        else:
            print("   ❌ SHA-256 hash INCORRECT")
            print(f"      Expected: {expected_hash}")
            print(f"      Got: {data.get('properties', {}).get('sha256_hash') if data else 'None'}")
            all_passed = False
    else:
        print(f"   ❌ Failed to create/get test string: {response.status_code}")
        all_passed = False
    
    # 2. Check case-insensitive palindrome
    print("\n2. Case-Insensitive Palindrome Check:")
    test_cases = [
        ("Racecar", True),
        ("A man a plan a canal Panama", True),
        ("Hello", False),
        ("Madam", True),
        ("12321", True)
    ]
    
    for test_str, expected in test_cases:
        response = requests.post(f"{BASE_URL}/strings", json={"value": test_str})
        if response.status_code in [201, 409]:
            get_response = requests.get(f"{BASE_URL}/strings/{test_str}")
            if get_response.status_code == 200:
                data = get_response.json()
                actual = data.get('properties', {}).get('is_palindrome')
                if actual == expected:
                    print(f"   ✅ '{test_str}': {actual} (expected {expected})")
                else:
                    print(f"   ❌ '{test_str}': {actual} (expected {expected})")
                    all_passed = False
            else:
                print(f"   ❌ Failed to get '{test_str}': {get_response.status_code}")
                all_passed = False
        else:
            print(f"   ❌ Failed to create '{test_str}': {response.status_code}")
            all_passed = False
    
    # 3. Check HTTP status codes
    print("\n3. HTTP Status Codes Verification:")
    status_checks = [
        ("POST new string", 201, lambda: requests.post(f"{BASE_URL}/strings", json={"value": f"new_{uuid.uuid4().hex[:8]}"})),
        ("POST duplicate", 409, lambda: requests.post(f"{BASE_URL}/strings", json={"value": "test_duplicate"})),
        ("GET non-existent", 404, lambda: requests.get(f"{BASE_URL}/strings/nonexistent_123")),
        ("DELETE non-existent", 404, lambda: requests.delete(f"{BASE_URL}/strings/nonexistent_123")),
        ("Missing value", 400, lambda: requests.post(f"{BASE_URL}/strings", json={"wrong": "field"})),
        ("Invalid type", 422, lambda: requests.post(f"{BASE_URL}/strings", json={"value": 123}))
    ]
    
    # Ensure duplicate exists
    requests.post(f"{BASE_URL}/strings", json={"value": "test_duplicate"})
    
    for desc, expected, request_func in status_checks:
        response = request_func()
        if response.status_code == expected:
            print(f"   ✅ {desc}: {expected}")
        else:
            print(f"   ❌ {desc}: expected {expected}, got {response.status_code}")
            all_passed = False
    
    # 4. Check URL endpoints are accessible
    print("\n4. Endpoint Accessibility:")
    endpoints = [
        ("POST /strings", lambda: requests.post(f"{BASE_URL}/strings", json={"value": "test_endpoint"})),
        ("GET /strings/{value}", lambda: requests.get(f"{BASE_URL}/strings/test_endpoint")),
        ("GET /strings?filter", lambda: requests.get(f"{BASE_URL}/strings?is_palindrome=true")),
        ("GET /strings/filter-by-natural-language", lambda: requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query=test")),
        ("DELETE /strings/{value}", lambda: requests.delete(f"{BASE_URL}/strings/test_endpoint"))
    ]
    
    for endpoint_name, request_func in endpoints:
        response = request_func()
        if response.status_code not in [405]:  # 405 is the main failure we saw
            print(f"   ✅ {endpoint_name}: accessible")
        else:
            print(f"   ❌ {endpoint_name}: 405 Method Not Allowed")
            all_passed = False
    
    return all_passed

def main():
    """
    Main test execution
    """
    print("🤖 BOT COMPATIBILITY TEST SUITE")
    print("This test EXACTLY matches the bot's requirements and format")
    print()
    
    # First, verify critical requirements
    print("STEP 1: Verifying critical requirements...")
    critical_ok = verify_critical_requirements()
    
    if not critical_ok:
        print("\n❌ CRITICAL REQUIREMENTS FAILED!")
        print("Fix these issues before running the full test suite.")
        return
    
    print("\n✅ ALL CRITICAL REQUIREMENTS PASSED!")
    print("Proceeding with full test suite...")
    
    # Run the main bot test suite
    print("\n" + "="*60)
    print("STEP 2: Running main test suite...")
    print("="*60)
    
    final_score = run_bot_tests()
    
    # Final assessment
    print(f"\n🎯 FINAL BOT COMPATIBILITY SCORE: {final_score}/100")
    
    if final_score >= 95:
        print("✅ PERFECT! Your API is ready for submission.")
        print("   The bot should give you a high score.")
    elif final_score >= 80:
        print("⚠️  GOOD! Minor issues but should pass.")
    elif final_score >= 60:
        print("❌ RISKY! Significant issues need fixing.")
    else:
        print("💥 CRITICAL! Major failures detected.")
    
    # Additional verification
    print(f"\n🔧 FINAL CHECKS:")
    print(f"1. Ensure your server is running at: {BASE_URL}")
    print(f"2. Test from a different network/device if possible")
    print(f"3. Verify no firewall/port issues")
    print(f"4. Make sure all recent code changes are deployed")

if __name__ == "__main__":
    main()