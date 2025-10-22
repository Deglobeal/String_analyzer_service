import requests
import hashlib
import uuid
import json

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def test_bot_endpoints():
    """
    Test ONLY the endpoints that the bot will test
    """
    print("🤖 FINAL BOT ENDPOINT TEST")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")
    print()
    
    results = {}
    
    # === POST /strings ===
    print("1. Testing POST /strings...")
    test_string = f"bot_test_{uuid.uuid4().hex[:8]}"
    
    # Test 1.1: Successful creation
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string}, timeout=10)
    results["POST_new"] = response.status_code == 201
    print(f"   POST new string: {response.status_code} (expected: 201) - {'✅' if response.status_code == 201 else '❌'}")
    
    if response.status_code == 201:
        data = response.json()
        # Verify SHA-256
        expected_hash = hashlib.sha256(test_string.encode()).hexdigest()
        actual_hash = data.get('properties', {}).get('sha256_hash')
        results["SHA256_correct"] = actual_hash == expected_hash
        print(f"   SHA-256 correct: {'✅' if actual_hash == expected_hash else '❌'}")
    
    # Test 1.2: Duplicate string
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string}, timeout=10)
    results["POST_duplicate"] = response.status_code == 409
    print(f"   POST duplicate: {response.status_code} (expected: 409) - {'✅' if response.status_code == 409 else '❌'}")
    
    # Test 1.3: Missing value field
    response = requests.post(f"{BASE_URL}/strings", json={"wrong_field": "test"}, timeout=10)
    results["POST_missing_value"] = response.status_code == 400
    print(f"   POST missing value: {response.status_code} (expected: 400) - {'✅' if response.status_code == 400 else '❌'}")
    
    # Test 1.4: Invalid data type
    response = requests.post(f"{BASE_URL}/strings", json={"value": 123}, timeout=10)
    results["POST_invalid_type"] = response.status_code == 422
    print(f"   POST invalid type: {response.status_code} (expected: 422) - {'✅' if response.status_code == 422 else '❌'}")
    
    # === GET /strings/{string_value} ===
    print("\n2. Testing GET /strings/{string_value}...")
    
    # Test 2.1: Non-existent string
    response = requests.get(f"{BASE_URL}/strings/nonexistent_string_12345", timeout=10)
    results["GET_nonexistent"] = response.status_code == 404
    print(f"   GET non-existent: {response.status_code} (expected: 404) - {'✅' if response.status_code == 404 else '❌'}")
    
    # Test 2.2: Existing string
    response = requests.get(f"{BASE_URL}/strings/{test_string}", timeout=10)
    results["GET_existing"] = response.status_code == 200
    print(f"   GET existing: {response.status_code} (expected: 200) - {'✅' if response.status_code == 200 else '❌'}")
    
    # === GET /strings with filters ===
    print("\n3. Testing GET /strings with filters...")
    
    # Create some test data
    test_strings = [f"filter_test_{i}_{uuid.uuid4().hex[:4]}" for i in range(3)]
    for s in test_strings:
        try:
            requests.post(f"{BASE_URL}/strings", json={"value": s}, timeout=5)
        except:
            pass
    
    # Test various filters
    filter_tests = [
        ("is_palindrome=true", "Palindrome filter"),
        ("min_length=5&max_length=20", "Length filters"),
        ("word_count=1", "Word count filter"),
        ("contains_character=a", "Character filter"),
        ("is_palindrome=true&min_length=1", "Combined filters")
    ]
    
    filter_results = []
    for filter_query, desc in filter_tests:
        response = requests.get(f"{BASE_URL}/strings?{filter_query}", timeout=10)
        success = response.status_code == 200
        filter_results.append(success)
        print(f"   {desc}: {response.status_code} - {'✅' if success else '❌'}")
    
    results["GET_filters"] = all(filter_results)
    
    # === GET /strings/filter-by-natural-language ===
    print("\n4. Testing GET /strings/filter-by-natural-language...")
    
    nl_queries = [
        "all single word palindromic strings",
        "strings longer than 5 characters",
        "palindromic strings that contain the letter a",
        "strings containing the letter e"
    ]
    
    nl_results = []
    for query in nl_queries:
        response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}", timeout=10)
        success = response.status_code == 200
        nl_results.append(success)
        print(f"   Query '{query}': {response.status_code} - {'✅' if success else '❌'}")
    
    results["GET_natural_language"] = all(nl_results)
    
    # === DELETE /strings/{string_value} ===
    print("\n5. Testing DELETE /strings/{string_value}...")
    
    # Test 5.1: Delete existing
    delete_string = f"delete_test_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/strings", json={"value": delete_string}, timeout=10)
    
    response = requests.delete(f"{BASE_URL}/strings/{delete_string}", timeout=10)
    results["DELETE_existing"] = response.status_code == 204
    print(f"   DELETE existing: {response.status_code} (expected: 204) - {'✅' if response.status_code == 204 else '❌'}")
    
    # Test 5.2: Delete non-existent
    response = requests.delete(f"{BASE_URL}/strings/nonexistent_delete_123", timeout=10)
    results["DELETE_nonexistent"] = response.status_code == 404
    print(f"   DELETE non-existent: {response.status_code} (expected: 404) - {'✅' if response.status_code == 404 else '❌'}")
    
    # === Final Results ===
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 SCORE: {passed_tests}/{total_tests} tests passed")
    
    # Calculate estimated bot score
    # Bot scoring:
    # POST: 25 points (5+5+2+3 = 15 for status codes + 10 for SHA256)
    # GET specific: 15 points (5+10)
    # GET filters: 25 points (5 filters × 5 points each)
    # Natural language: 20 points (4 queries × 5 points each) 
    # DELETE: 15 points (10+5)
    
    estimated_score = 0
    
    # POST scoring (25 points)
    if results.get("POST_new") and results.get("SHA256_correct", False):
        estimated_score += 5  # Successful creation
    if results.get("POST_duplicate"):
        estimated_score += 5  # Duplicate
    if results.get("POST_missing_value"):
        estimated_score += 2  # Missing value
    if results.get("POST_invalid_type"):
        estimated_score += 3  # Invalid type
    # SHA256 is part of POST_new check
    
    # GET specific scoring (15 points)
    if results.get("GET_nonexistent"):
        estimated_score += 5  # Non-existent
    if results.get("GET_existing"):
        estimated_score += 10  # Existing
    
    # GET filters scoring (25 points)
    if results.get("GET_filters"):
        estimated_score += 25  # All filters working
    
    # Natural language scoring (20 points)
    if results.get("GET_natural_language"):
        estimated_score += 20  # All queries working
    
    # DELETE scoring (15 points)
    if results.get("DELETE_existing"):
        estimated_score += 10  # Delete existing
    if results.get("DELETE_nonexistent"):
        estimated_score += 5  # Delete non-existent
    
    print(f"\n🎯 ESTIMATED BOT SCORE: {estimated_score}/100")
    
    if estimated_score >= 95:
        print("🚀 EXCELLENT! Your Railway deployment should pass the bot test.")
        print("   You can submit this URL with confidence.")
    elif estimated_score >= 80:
        print("⚠️  GOOD! Minor issues but should pass.")
    elif estimated_score >= 60:
        print("❌ RISKY! Some significant issues.")
    else:
        print("💥 CRITICAL! Major issues need fixing.")
    
    return estimated_score

def verify_palindrome_case_insensitive():
    """Specifically test case-insensitive palindrome requirement"""
    print("\n🔍 VERIFYING CASE-INSENSITIVE PALINDROME")
    print("=" * 50)
    
    test_cases = [
        ("Racecar", True),
        ("A man a plan a canal Panama", True),
        ("Hello", False),
        ("Madam", True),
    ]
    
    all_correct = True
    for test_str, expected in test_cases:
        try:
            # Create or get the string
            response = requests.post(f"{BASE_URL}/strings", json={"value": test_str}, timeout=10)
            if response.status_code in [201, 409]:
                # Get the analysis
                get_response = requests.get(f"{BASE_URL}/strings/{test_str}", timeout=10)
                if get_response.status_code == 200:
                    data = get_response.json()
                    actual = data.get('properties', {}).get('is_palindrome')
                    if actual == expected:
                        print(f"✅ '{test_str}': {actual} (expected {expected})")
                    else:
                        print(f"❌ '{test_str}': {actual} (expected {expected})")
                        all_correct = False
                else:
                    print(f"❌ Failed to get '{test_str}': {get_response.status_code}")
                    all_correct = False
            else:
                print(f"❌ Failed to create '{test_str}': {response.status_code}")
                all_correct = False
        except Exception as e:
            print(f"❌ Error testing '{test_str}': {e}")
            all_correct = False
    
    return all_correct

def main():
    """Main test execution"""
    print("🤖 ULTIMATE BOT COMPATIBILITY TEST")
    print("This test ONLY checks what the bot will check")
    print()
    
    # Test palindrome case sensitivity (critical requirement)
    print("STEP 1: Testing critical requirements...")
    palindrome_ok = verify_palindrome_case_insensitive()
    
    if not palindrome_ok:
        print("\n❌ CRITICAL: Palindrome check failed!")
        return
    
    print("\n✅ Critical requirements passed!")
    
    # Run main bot endpoint tests
    print("\n" + "="*60)
    print("STEP 2: Testing all bot endpoints...")
    print("="*60)
    
    final_score = test_bot_endpoints()
    
    # Final recommendation
    print(f"\n💡 RECOMMENDATION:")
    if final_score >= 95:
        print("   SUBMIT NOW! Your API is ready for the bot.")
        print(f"   URL: {BASE_URL}")
    else:
        print("   FIX ISSUES before submitting.")
        print("   Check the failed tests above.")

if __name__ == "__main__":
    main()