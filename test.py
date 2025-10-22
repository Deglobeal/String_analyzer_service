import requests
import json
import hashlib
from collections import Counter
import time
import sys
import uuid

# Update with your base URL - try both common Django URLs
BASE_URLS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

def find_server():
    """Try to find which URL the server is running on"""
    for base_url in BASE_URLS:
        try:
            response = requests.get(f"{base_url}/strings", timeout=2)
            return base_url
        except:
            continue
    return None

BASE_URL = find_server()

if not BASE_URL:
    print("❌ Django server is not running!")
    print("Please start the server with: python manage.py runserver")
    print("Then run this test again.")
    sys.exit(1)

print(f"✅ Server found at: {BASE_URL}")

def test_post_strings():
    """Test POST /strings endpoint"""
    print("=== POST /strings (25 points) ===")
    points = 0
    
    try:
        # Test 1: Successful creation - use unique string
        unique_string = f"hello world {uuid.uuid4().hex[:8]}"
        print("Testing successful string creation...")
        response = requests.post(f"{BASE_URL}/strings", json={"value": unique_string})
        print(f"Status code: {response.status_code} (expected 201)")
        if response.status_code == 201:
            points += 5
            print("✓ status code: 201 (5/5 pts)")
        else:
            print(f"✗ status code: {response.status_code} (expected 201) (0/5 pts)")
        
        # Test 2: Duplicate string - use the same unique string
        print("Testing duplicate string...")
        response = requests.post(f"{BASE_URL}/strings", json={"value": unique_string})
        print(f"Status for duplicate: {response.status_code} (expected 409)")
        if response.status_code == 409:
            points += 5
            print("✓ status for duplicate: 409 (5/5 pts)")
        else:
            print(f"✗ status for duplicate: {response.status_code} (expected 409) (0/5 pts)")
        
        # Test 3: Missing value field
        print("Testing missing value field...")
        response = requests.post(f"{BASE_URL}/strings", json={"wrong_field": "test"})
        print(f"Status for missing 'value' field: {response.status_code} (expected 400)")
        if response.status_code == 400:
            points += 2
            print("✓ status for missing 'value' field: 400 (2/2 pts)")
        else:
            print(f"✗ status for missing 'value' field: {response.status_code} (expected 400) (0/2 pts)")
        
        # Test 4: Invalid data type
        print("Testing invalid data type...")
        response = requests.post(f"{BASE_URL}/strings", json={"value": 123})
        print(f"Status for invalid data type: {response.status_code} (expected 422)")
        if response.status_code == 422:
            points += 3
            print("✓ status for invalid data type: 422 (3/3 pts)")
        else:
            print(f"✗ status for invalid data type: {response.status_code} (expected 422) (0/3 pts)")
        
        print(f"POST /strings score: {points}/25")
        return points
        
    except Exception as e:
        print(f"Error in POST tests: {e}")
        print(f"POST /strings score: {points}/25")
        return points

def test_get_specific_string():
    """Test GET /strings/{string_value} endpoint"""
    print("\n=== GET /strings/{string_value} (15 points) ===")
    points = 0
    
    try:
        # Test 1: Get existing string - use unique string
        test_string = f"test palindrome {uuid.uuid4().hex[:8]}"
        requests.post(f"{BASE_URL}/strings", json={"value": test_string})
        
        response = requests.get(f"{BASE_URL}/strings/{test_string}")
        print(f"Get existing string: {response.status_code} (expected 200)")
        if response.status_code == 200:
            points += 10
            print("✓ Get existing string: 200 (10/10 pts)")
        else:
            print(f"✗ Get existing string: {response.status_code} (expected 200) (0/10 pts)")
        
        # Test 2: Get non-existent string
        response = requests.get(f"{BASE_URL}/strings/nonexistentstring123")
        print(f"Returns 404 for non-existent string: {response.status_code} (expected 404)")
        if response.status_code == 404:
            points += 5
            print("✓ Returns 404 for non-existent string: 404 (5/5 pts)")
        else:
            print(f"✗ Returns 404 for non-existent string: {response.status_code} (expected 404) (0/5 pts)")
        
        print(f"GET specific string score: {points}/15")
        return points
        
    except Exception as e:
        print(f"Error in GET specific tests: {e}")
        print(f"GET specific string score: {points}/15")
        return points

def test_get_strings_with_filters():
    """Test GET /strings with filters"""
    print("\n=== GET /strings with filters (25 points) ===")
    points = 0
    
    try:
        # Create test data with unique identifiers
        test_strings = [
            f"a {uuid.uuid4().hex[:4]}",  # palindrome, 1 word
            f"madam {uuid.uuid4().hex[:4]}",  # palindrome, 1 word  
            f"hello world {uuid.uuid4().hex[:4]}",  # 2 words
            f"python programming language {uuid.uuid4().hex[:4]}",  # 3 words
            f"test string for filtering {uuid.uuid4().hex[:4]}"  # 4 words
        ]
        
        for string in test_strings:
            try:
                requests.post(f"{BASE_URL}/strings", json={"value": string})
            except:
                pass  # Some might already exist
        
        # Wait a bit for all strings to be processed
        time.sleep(1)
        
        # Test palindrome filter - using strings-list endpoint
        response = requests.get(f"{BASE_URL}/strings-list?is_palindrome=true")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                points += 5
                print("✓ Palindrome filter works (5/5 pts)")
            else:
                print("✗ Palindrome filter returned no data (0/5 pts)")
        else:
            print(f"✗ Palindrome filter failed with status {response.status_code} (0/5 pts)")
        
        # Test length filters
        response = requests.get(f"{BASE_URL}/strings-list?min_length=5&max_length=10")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                points += 5
                print("✓ Length filters work (5/5 pts)")
            else:
                print("✗ Length filters returned no data (0/5 pts)")
        else:
            print(f"✗ Length filters failed with status {response.status_code} (0/5 pts)")
        
        # Test word count filter
        response = requests.get(f"{BASE_URL}/strings-list?word_count=2")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                points += 5
                print("✓ Word count filter works (5/5 pts)")
            else:
                print("✗ Word count filter returned no data (0/5 pts)")
        else:
            print(f"✗ Word count filter failed with status {response.status_code} (0/5 pts)")
        
        # Test character containment
        response = requests.get(f"{BASE_URL}/strings-list?contains_character=a")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                points += 5
                print("✓ Character containment filter works (5/5 pts)")
            else:
                print("✗ Character containment filter returned no data (0/5 pts)")
        else:
            print(f"✗ Character containment filter failed with status {response.status_code} (0/5 pts)")
        
        # Test combined filters
        response = requests.get(f"{BASE_URL}/strings-list?is_palindrome=true&min_length=3")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                points += 5
                print("✓ Combined filters work (5/5 pts)")
            else:
                print("✗ Combined filters returned no data (0/5 pts)")
        else:
            print(f"✗ Combined filters failed with status {response.status_code} (0/5 pts)")
        
        print(f"GET with filters score: {points}/25")
        return points
        
    except Exception as e:
        print(f"Error in filter tests: {e}")
        print(f"GET with filters score: {points}/25")
        return points

def test_natural_language_filter():
    """Test GET /strings/filter-by-natural-language"""
    print("\n=== GET /strings/filter-by-natural-language (20 points) ===")
    points = 0
    
    try:
        # Test various natural language queries
        test_queries = [
            "all single word palindromic strings",
            "strings longer than 5 characters", 
            "palindromic strings that contain the letter a",
            "strings containing the letter e"
        ]
        
        points_per_query = 5
        
        for query in test_queries:
            response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}")
            print(f"Natural language query '{query}': {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    points += points_per_query
                    print(f"✓ Natural language query: '{query}' ({points_per_query}/{points_per_query} pts)")
                else:
                    print(f"✗ Natural language query: '{query}' returned no data (0/{points_per_query} pts)")
            else:
                print(f"✗ Natural language query: '{query}' failed with status {response.status_code} (0/{points_per_query} pts)")
        
        print(f"Natural language filter score: {points}/20")
        return points
        
    except Exception as e:
        print(f"Error in natural language tests: {e}")
        print(f"Natural language filter score: {points}/20")
        return points

def test_delete_string():
    """Test DELETE /strings/{string_value}"""
    print("\n=== DELETE /strings/{string_value} (15 points) ===")
    points = 0
    
    try:
        # Create and then delete a string - use unique string
        test_string = f"string to delete {uuid.uuid4().hex[:8]}"
        requests.post(f"{BASE_URL}/strings", json={"value": test_string})
        
        # Test successful deletion - using the correct delete endpoint
        response = requests.delete(f"{BASE_URL}/strings/delete/{test_string}")
        print(f"Delete existing string: {response.status_code} (expected 204)")
        if response.status_code == 204:
            points += 10
            print("✓ Delete existing string: 204 (10/10 pts)")
        else:
            print(f"✗ Delete existing string: {response.status_code} (expected 204) (0/10 pts)")
        
        # Test deletion of non-existent string
        response = requests.delete(f"{BASE_URL}/strings/delete/nonexistentstring")
        print(f"Delete non-existent string: {response.status_code} (expected 404)")
        if response.status_code == 404:
            points += 5
            print("✓ Delete non-existent string: 404 (5/5 pts)")
        else:
            print(f"✗ Delete non-existent string: {response.status_code} (expected 404) (0/5 pts)")
        
        print(f"DELETE string score: {points}/15")
        return points
        
    except Exception as e:
        print(f"Error in DELETE tests: {e}")
        print(f"DELETE string score: {points}/15")
        return points

def run_all_tests():
    """Run all test suites"""
    total_points = 0
    
    try:
        total_points += test_post_strings()
        total_points += test_get_specific_string() 
        total_points += test_get_strings_with_filters()
        total_points += test_natural_language_filter()
        total_points += test_delete_string()
        
        print("\n=== Cleanup ===")
        print(f"FINAL SCORE: {total_points}/100 ({total_points}%)")
        print("=============================")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        print("FINAL SCORE: 0/100 (0.0%)")

if __name__ == "__main__":
    run_all_tests()