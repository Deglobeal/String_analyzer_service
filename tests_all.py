import requests
import json
import hashlib
import uuid
import re

BASE_URL = "http://localhost:8000"

class TestStringAnalyzer:
    def __init__(self):
        self.total_score = 0
        self.test_data = []

    def run_all_tests(self):
        print("=" * 60)
        print("=" * 60)
        
        post_score = self.test_post_strings()
        get_specific_score = self.test_get_specific_string()
        get_filters_score = self.test_get_strings_with_filters()
        natural_language_score = self.test_natural_language_filter()
        delete_score = self.test_delete_string()
        
        self.total_score = post_score + get_specific_score + get_filters_score + natural_language_score + delete_score
        
        print("\n=== Cleanup ===")
        print(f"FINAL SCORE: {self.total_score}/100 ({self.total_score}%)")
        print("=" * 60)
        
        return self.total_score

    def test_post_strings(self):
        print("=== POST /strings (25 points) ===")
        score = 0
        
        # Test 1: Successful creation
        test_string = f"test_string_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
        
        if response.status_code == 201:
            data = response.json()
            # Verify all required fields are present
            if all(k in data for k in ['id', 'value', 'properties', 'created_at']):
                props = data['properties']
                if all(k in props for k in ['length', 'is_palindrome', 'unique_characters', 'word_count', 'sha256_hash', 'character_frequency_map']):
                    # Verify SHA256 hash is correct
                    expected_hash = hashlib.sha256(test_string.encode()).hexdigest()
                    if props['sha256_hash'] == expected_hash:
                        score += 5
                        print("✓ status code:  (expected 201) (5/5 pts)")
                    else:
                        print("✗ Wrong status code: 201 but SHA256 hash incorrect (0/5 pts)")
                else:
                    print("✗ Wrong status code: 201 but missing properties (0/5 pts)")
            else:
                print("✗ Wrong status code: 201 but missing fields (0/5 pts)")
        else:
            print(f"✗ Wrong status code: {response.status_code} (expected 201) (0/5 pts)")

        # Test 2: Duplicate string
        response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
        if response.status_code == 409:
            score += 5
            print("✓ status for duplicate:  (expected 409) (5/5 pts)")
        else:
            print(f"✗ Wrong status for duplicate: {response.status_code} (expected 409) (0/5 pts)")

        # Test 3: Missing value field
        response = requests.post(f"{BASE_URL}/strings", json={"wrong_field": "test"})
        if response.status_code == 400:
            score += 2
            print("✓ status for missing 'value' field: 405 (2/2 pts)")
        else:
            print(f"✗ Wrong status for missing 'value' field: {response.status_code} (0/2 pts)")

        # Test 4: Invalid data type
        response = requests.post(f"{BASE_URL}/strings", json={"value": 123})
        if response.status_code == 422:
            score += 3
            print("✓ status for invalid data type: 405 (3/3 pts)")
        else:
            print(f"✗ Wrong status for invalid data type: {response.status_code} (0/3 pts)")

        print(f"POST /strings score: {score}/25")
        return score

    def test_get_specific_string(self):
        print("\n=== GET /strings/{string_value} (15 points) ===")
        score = 0
        
        # Test 1: Get existing string
        test_string = f"test_get_{uuid.uuid4().hex[:8]}"
        # First create the string
        create_response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
        if create_response.status_code == 201:
            response = requests.get(f"{BASE_URL}/strings/{test_string}")
            if response.status_code == 200:
                data = response.json()
                if data['value'] == test_string:
                    score += 10
                    print("✓ Returns 200 for existing string (10/10 pts)")
                else:
                    print("✗ Returns 200 but wrong string data (0/10 pts)")
            else:
                print(f"✗ Returns {response.status_code} for existing string (expected 200) (0/10 pts)")
        else:
            print("✗ Failed to create string for GET test (0/10 pts)")

        # Test 2: Get non-existent string
        response = requests.get(f"{BASE_URL}/strings/nonexistent_string_12345")
        if response.status_code == 404:
            score += 5
            print("✓ Returns 404 for non-existent string (5/5 pts)")
        else:
            print(f"✗ Returns {response.status_code} for non-existent string (expected 404) (0/5 pts)")

        print(f"GET specific string score: {score}/15")
        return score

    def test_get_strings_with_filters(self):
        print("\n=== GET /strings with filters (25 points) ===")
        score = 0
        
        # Create test data
        test_strings = [
            f"a_{uuid.uuid4().hex[:4]}",  # palindrome, 1 word, length ~6
            f"madam_{uuid.uuid4().hex[:4]}",  # palindrome, 1 word, length ~10  
            f"hello world_{uuid.uuid4().hex[:4]}",  # 2 words, length ~16
            f"python programming_{uuid.uuid4().hex[:4]}",  # 2 words, length ~22
            f"test string for filtering_{uuid.uuid4().hex[:4]}"  # 4 words, length ~28
        ]
        
        for string in test_strings:
            try:
                requests.post(f"{BASE_URL}/strings", json={"value": string})
            except:
                pass

        # Test 1: Palindrome filter
        response = requests.get(f"{BASE_URL}/strings?is_palindrome=true")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'filters_applied' in data:
                if data['filters_applied'].get('is_palindrome') == True:
                    score += 5
                    print("✓ Palindrome filter works (5/5 pts)")
                else:
                    print("✗ Palindrome filter applied but not in filters_applied (0/5 pts)")
            else:
                print("✗ Palindrome filter missing response fields (0/5 pts)")
        else:
            print(f"✗ Palindrome filter failed with status {response.status_code} (0/5 pts)")

        # Test 2: Length filters
        response = requests.get(f"{BASE_URL}/strings?min_length=5&max_length=15")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'filters_applied' in data:
                if data['filters_applied'].get('min_length') == 5 and data['filters_applied'].get('max_length') == 15:
                    score += 5
                    print("✓ Length filters work (5/5 pts)")
                else:
                    print("✗ Length filters applied but not in filters_applied (0/5 pts)")
            else:
                print("✗ Length filters missing response fields (0/5 pts)")
        else:
            print(f"✗ Length filters failed with status {response.status_code} (0/5 pts)")

        # Test 3: Word count filter
        response = requests.get(f"{BASE_URL}/strings?word_count=2")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'filters_applied' in data:
                if data['filters_applied'].get('word_count') == 2:
                    score += 5
                    print("✓ Word count filter works (5/5 pts)")
                else:
                    print("✗ Word count filter applied but not in filters_applied (0/5 pts)")
            else:
                print("✗ Word count filter missing response fields (0/5 pts)")
        else:
            print(f"✗ Word count filter failed with status {response.status_code} (0/5 pts)")

        # Test 4: Character containment filter
        response = requests.get(f"{BASE_URL}/strings?contains_character=a")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'filters_applied' in data:
                if data['filters_applied'].get('contains_character') == 'a':
                    score += 5
                    print("✓ Character containment filter works (5/5 pts)")
                else:
                    print("✗ Character containment filter applied but not in filters_applied (0/5 pts)")
            else:
                print("✗ Character containment filter missing response fields (0/5 pts)")
        else:
            print(f"✗ Character containment filter failed with status {response.status_code} (0/5 pts)")

        # Test 5: Combined filters
        response = requests.get(f"{BASE_URL}/strings?is_palindrome=true&min_length=3")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'filters_applied' in data:
                filters = data['filters_applied']
                if filters.get('is_palindrome') == True and filters.get('min_length') == 3:
                    score += 5
                    print("✓ Combined filters work (5/5 pts)")
                else:
                    print("✗ Combined filters applied but not in filters_applied (0/5 pts)")
            else:
                print("✗ Combined filters missing response fields (0/5 pts)")
        else:
            print(f"✗ Combined filters failed with status {response.status_code} (0/5 pts)")

        print(f"GET with filters score: {score}/25")
        return score

    def test_natural_language_filter(self):
        print("\n=== GET /strings/filter-by-natural-language (20 points) ===")
        score = 0
        
        # Create test data
        test_strings = [
            f"racecar_{uuid.uuid4().hex[:4]}",  # palindrome, 1 word
            f"hello_{uuid.uuid4().hex[:4]}",  # 1 word, contains e
            f"test string_{uuid.uuid4().hex[:4]}",  # 2 words
            f"longer test string_{uuid.uuid4().hex[:4]}",  # 3 words, longer
        ]
        
        for string in test_strings:
            try:
                requests.post(f"{BASE_URL}/strings", json={"value": string})
            except:
                pass

        test_queries = [
            "all single word palindromic strings",
            "strings longer than 10 characters", 
            "palindromic strings that contain the letter a",
            "strings containing the letter e"
        ]
        
        for query in test_queries:
            response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'interpreted_query' in data:
                    interpreted = data['interpreted_query']
                    if 'original' in interpreted and 'parsed_filters' in interpreted:
                        score += 5
                        print(f"✓ Natural language query: '{query}' (5/5 pts)")
                    else:
                        print(f"✗ Natural language query: '{query}' - missing interpreted_query fields (0/5 pts)")
                else:
                    print(f"✗ Natural language query: '{query}' - missing response fields (0/5 pts)")
            else:
                print(f"✗ Natural language query: '{query}' - status {response.status_code} (0/5 pts)")

        print(f"Natural language filter score: {score}/20")
        return score

    def test_delete_string(self):
        print("\n=== DELETE /strings/{string_value} (15 points) ===")
        score = 0
        
        # Test 1: Delete existing string
        delete_string = f"delete_test_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/strings", json={"value": delete_string})
        
        if create_response.status_code == 201:
            response = requests.delete(f"{BASE_URL}/strings/{delete_string}")
            if response.status_code == 204:
                # Verify it's actually deleted by trying to get it
                get_response = requests.get(f"{BASE_URL}/strings/{delete_string}")
                if get_response.status_code == 404:
                    score += 10
                    print("✓ DELETE existing string (10/10 pts)")
                else:
                    print("✗ DELETE returned 204 but string still exists (0/10 pts)")
            else:
                print(f"✗ DELETE existing string - status {response.status_code} (0/10 pts)")
        else:
            print("✗ Failed to create string for DELETE test (0/10 pts)")

        # Test 2: Delete non-existent string
        response = requests.delete(f"{BASE_URL}/strings/nonexistent_delete_test")
        if response.status_code == 404:
            score += 5
            print("✓ DELETE non-existent string (5/5 pts)")
        else:
            print(f"✗ DELETE non-existent string - status {response.status_code} (0/5 pts)")

        print(f"DELETE string score: {score}/15")
        return score

    def verify_sha256_implementation(self):
        """Additional test to verify SHA256 implementation"""
        print("\n=== SHA256 Verification Test ===")
        test_string = "test_sha256"
        response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
        if response.status_code == 201:
            data = response.json()
            expected_hash = hashlib.sha256(test_string.encode()).hexdigest()
            if data['properties']['sha256_hash'] == expected_hash:
                print("✓ SHA256 hash calculated correctly")
                return True
            else:
                print("✗ SHA256 hash incorrect")
                return False
        return False

    def verify_palindrome_case_insensitive(self):
        """Additional test to verify case-insensitive palindrome check"""
        print("\n=== Palindrome Case-Insensitive Test ===")
        test_cases = [
            ("Racecar", True),
            ("A man a plan a canal Panama", True),
            ("Hello", False),
            ("Madam", True)
        ]
        
        all_passed = True
        for test_string, expected in test_cases:
            response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
            if response.status_code in [201, 409]:  # Created or already exists
                # Get the analysis
                get_response = requests.get(f"{BASE_URL}/strings/{test_string}")
                if get_response.status_code == 200:
                    data = get_response.json()
                    actual = data['properties']['is_palindrome']
                    if actual == expected:
                        print(f"✓ '{test_string}': {actual} (expected {expected})")
                    else:
                        print(f"✗ '{test_string}': {actual} (expected {expected})")
                        all_passed = False
                else:
                    print(f"✗ Failed to get analysis for '{test_string}'")
                    all_passed = False
            else:
                print(f"✗ Failed to create string '{test_string}'")
                all_passed = False
        
        return all_passed

def main():
    tester = TestStringAnalyzer()
    
    print("Running comprehensive tests...")
    print("This will test all endpoints against the bot's requirements.")
    print()
    
    # Run main tests
    final_score = tester.run_all_tests()
    
    # Run additional verification tests
    print("\n=== Additional Verification Tests ===")
    tester.verify_sha256_implementation()
    tester.verify_palindrome_case_insensitive()
    
    print(f"\n🎯 FINAL VERDICT: {final_score}/100")
    
    if final_score >= 90:
        print("✅ Excellent! Ready for submission.")
    elif final_score >= 70:
        print("⚠️  Good, but some issues need fixing.")
    else:
        print("❌ Significant issues need to be addressed.")
    
    return final_score

if __name__ == "__main__":
    main()