import requests
import hashlib
import uuid
import json

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def test_bot_endpoints():
    """
    Test ONLY the endpoints that the bot will actually test
    The bot doesn't care about the root URL - only the specific API endpoints
    """
    print("🤖 BOT ENDPOINT TEST (Ignore root URL 404)")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")
    print()
    
    # Test each endpoint the bot will test
    endpoints_to_test = [
        "POST /strings",
        "GET /strings/{string_value}", 
        "GET /strings?filters",
        "GET /strings/filter-by-natural-language",
        "DELETE /strings/{string_value}"
    ]
    
    print("Testing endpoints the bot will actually check:")
    print("-" * 50)
    
    test_string = f"bot_test_{uuid.uuid4().hex[:8]}"
    all_passed = True
    
    # 1. POST /strings
    print("\n1. POST /strings")
    print("-" * 30)
    
    # 1.1 Successful creation
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    print(f"   New string: {response.status_code} (expected: 201) - {'✅' if response.status_code == 201 else '❌'}")
    if response.status_code != 201:
        all_passed = False
    
    # 1.2 Duplicate
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    print(f"   Duplicate: {response.status_code} (expected: 409) - {'✅' if response.status_code == 409 else '❌'}")
    if response.status_code != 409:
        all_passed = False
    
    # 1.3 Missing value
    response = requests.post(f"{BASE_URL}/strings", json={"wrong_field": "test"})
    print(f"   Missing value: {response.status_code} (expected: 400) - {'✅' if response.status_code == 400 else '❌'}")
    if response.status_code != 400:
        all_passed = False
    
    # 1.4 Invalid type
    response = requests.post(f"{BASE_URL}/strings", json={"value": 123})
    print(f"   Invalid type: {response.status_code} (expected: 422) - {'✅' if response.status_code == 422 else '❌'}")
    if response.status_code != 422:
        all_passed = False
    
    # 2. GET /strings/{string_value}
    print("\n2. GET /strings/{string_value}")
    print("-" * 30)
    
    # 2.1 Non-existent string
    response = requests.get(f"{BASE_URL}/strings/nonexistent_string_12345")
    print(f"   Non-existent: {response.status_code} (expected: 404) - {'✅' if response.status_code == 404 else '❌'}")
    if response.status_code != 404:
        all_passed = False
    
    # 2.2 Existing string
    response = requests.get(f"{BASE_URL}/strings/{test_string}")
    print(f"   Existing: {response.status_code} (expected: 200) - {'✅' if response.status_code == 200 else '❌'}")
    if response.status_code != 200:
        all_passed = False
    
    # 3. GET /strings with filters
    print("\n3. GET /strings with filters")
    print("-" * 30)
    
    filters = [
        "is_palindrome=true",
        "min_length=5&max_length=15", 
        "word_count=2",
        "contains_character=a",
        "is_palindrome=true&min_length=3"
    ]
    
    filter_passed = True
    for filter_query in filters:
        response = requests.get(f"{BASE_URL}/strings?{filter_query}")
        if response.status_code != 200:
            filter_passed = False
        print(f"   {filter_query}: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
    
    print(f"   All filters working: {'✅' if filter_passed else '❌'}")
    if not filter_passed:
        all_passed = False
    
    # 4. Natural Language Filter
    print("\n4. GET /strings/filter-by-natural-language")
    print("-" * 30)
    
    test_queries = [
        "all single word palindromic strings",
        "strings longer than 5 characters",
        "palindromic strings that contain the letter a",
        "strings containing the letter e"
    ]
    
    nl_passed = True
    for query in test_queries:
        response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}")
        if response.status_code == 200:
            data = response.json()
            filters_applied = len(data['interpreted_query']['parsed_filters']) > 0
            if not filters_applied:
                nl_passed = False
            status = "✅" if filters_applied else "❌"
            print(f"   '{query}': {len(data['data'])} results - {status}")
        else:
            nl_passed = False
            print(f"   '{query}': {response.status_code} - ❌")
    
    print(f"   All NL queries working: {'✅' if nl_passed else '❌'}")
    if not nl_passed:
        all_passed = False
    
    # 5. DELETE /strings/{string_value}
    print("\n5. DELETE /strings/{string_value}")
    print("-" * 30)
    
    # 5.1 Delete existing
    delete_test = f"delete_test_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/strings", json={"value": delete_test})
    response = requests.delete(f"{BASE_URL}/strings/{delete_test}")
    print(f"   Delete existing: {response.status_code} (expected: 204) - {'✅' if response.status_code == 204 else '❌'}")
    if response.status_code != 204:
        all_passed = False
    
    # 5.2 Delete non-existent
    response = requests.delete(f"{BASE_URL}/strings/nonexistent_delete_123")
    print(f"   Delete non-existent: {response.status_code} (expected: 404) - {'✅' if response.status_code == 404 else '❌'}")
    if response.status_code != 404:
        all_passed = False
    
    # FINAL RESULTS
    print("\n" + "=" * 60)
    print("🎯 FINAL BOT COMPATIBILITY ASSESSMENT")
    print("=" * 60)
    
    if all_passed:
        print("✅ ALL BOT ENDPOINTS ARE WORKING CORRECTLY!")
        print("🚀 You are READY for submission!")
        print()
        print("The bot will test these exact endpoints:")
        for endpoint in endpoints_to_test:
            print(f"   ✓ {endpoint}")
        print()
        print("💡 Submit this URL to the bot:")
        print(f"   {BASE_URL}")
    else:
        print("❌ Some endpoints need fixing before submission.")
        print("   Check the failed tests above.")

def verify_critical_requirements():
    """Verify the specific requirements mentioned by the bot"""
    print("\n🔍 VERIFYING CRITICAL REQUIREMENTS")
    print("=" * 50)
    
    # 1. SHA-256 hash calculation
    print("\n1. SHA-256 Hash:")
    test_string = "test_sha256"
    expected_hash = hashlib.sha256(test_string.encode()).hexdigest()
    
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    if response.status_code in [201, 409]:
        if response.status_code == 201:
            data = response.json()
        else:
            response = requests.get(f"{BASE_URL}/strings/{test_string}")
            data = response.json()
        
        actual_hash = data.get('properties', {}).get('sha256_hash')
        if actual_hash == expected_hash:
            print("   ✅ SHA-256 calculated correctly")
        else:
            print(f"   ❌ SHA-256 incorrect: expected {expected_hash}, got {actual_hash}")
    else:
        print(f"   ❌ Failed to test SHA-256: {response.status_code}")
    
    # 2. Case-insensitive palindrome
    print("\n2. Case-Insensitive Palindrome:")
    test_cases = [
        ("Racecar", True),
        ("A man a plan a canal Panama", True),
        ("Hello", False),
        ("Madam", True)
    ]
    
    all_correct = True
    for test_str, expected in test_cases:
        requests.post(f"{BASE_URL}/strings", json={"value": test_str})
        response = requests.get(f"{BASE_URL}/strings/{test_str}")
        if response.status_code == 200:
            data = response.json()
            actual = data.get('properties', {}).get('is_palindrome')
            if actual == expected:
                print(f"   ✅ '{test_str}': {actual}")
            else:
                print(f"   ❌ '{test_str}': {actual} (expected {expected})")
                all_correct = False
        else:
            print(f"   ❌ Failed to get '{test_str}': {response.status_code}")
            all_correct = False
    
    if all_correct:
        print("   ✅ All palindrome tests correct")
    else:
        print("   ❌ Some palindrome tests failed")
    
    # 3. Natural Language Parsing
    print("\n3. Natural Language Keyword Detection:")
    test_queries = [
        ("all single word palindromic strings", ["word_count=1", "is_palindrome=true"]),
        ("strings longer than 5 characters", ["min_length=6"]),
        ("palindromic strings that contain the letter a", ["is_palindrome=true", "contains_character=a"]),
        ("strings containing the letter e", ["contains_character=e"])
    ]
    
    nl_working = True
    for query, expected_filters in test_queries:
        response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}")
        if response.status_code == 200:
            data = response.json()
            parsed = data['interpreted_query']['parsed_filters']
            print(f"   '{query}': {parsed}")
            
            # Check if we got at least one expected filter
            has_expected = any(str(expected) in str(parsed) for expected in expected_filters)
            if has_expected:
                print("      ✅ Keywords detected")
            else:
                print("      ❌ Keywords not detected properly")
                nl_working = False
        else:
            print(f"   '{query}': ❌ Failed - {response.status_code}")
            nl_working = False
    
    if nl_working:
        print("   ✅ Natural language parsing working")
    else:
        print("   ❌ Natural language parsing needs improvement")

def main():
    """Main test execution"""
    print("🚀 ULTIMATE BOT COMPATIBILITY CHECK")
    print("This test ONLY checks what the bot will actually test")
    print("Ignore root URL 404 - the bot doesn't test it!")
    print()
    
    # Test all bot endpoints
    test_bot_endpoints()
    
    # Verify critical requirements
    print("\n" + "=" * 60)
    verify_critical_requirements()
    
    print("\n💡 FINAL RECOMMENDATION:")
    print("   If all endpoints above show ✅, you are READY to submit!")
    print(f"   Submission URL: {BASE_URL}")

if __name__ == "__main__":
    main()