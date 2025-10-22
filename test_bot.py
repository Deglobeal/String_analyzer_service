import requests
import json
import hashlib
import uuid

BASE_URL = "http://localhost:8000"

def run_tests():
    print("=" * 60)
    print("=" * 60)
    
    total_score = 0
    
    # === POST /strings (25 points) ===
    print("=== POST /strings (25 points) ===")
    post_score = 0
    
    # Test 1: Successful creation
    unique_str = f"test_{uuid.uuid4().hex[:8]}"
    response = requests.post(f"{BASE_URL}/strings", json={"value": unique_str})
    if response.status_code == 201:
        data = response.json()
        if all(k in data for k in ['id', 'value', 'properties', 'created_at']):
            post_score += 5
            print("✓ status code:  (expected 201) (5/5 pts)")
        else:
            print("✗ Wrong status code: 201 but missing fields (0/5 pts)")
    else:
        print(f"✗ Wrong status code: {response.status_code} (expected 201) (0/5 pts)")
    
    # Test 2: Duplicate string
    response = requests.post(f"{BASE_URL}/strings", json={"value": unique_str})
    if response.status_code == 409:
        post_score += 5
        print("✓ status for duplicate:  (expected 409) (5/5 pts)")
    else:
        print(f"✗ Wrong status for duplicate: {response.status_code} (expected 409) (0/5 pts)")
    
    # Test 3: Missing value field
    response = requests.post(f"{BASE_URL}/strings", json={"wrong_field": "test"})
    if response.status_code == 400:
        post_score += 2
        print("✓ status for missing 'value' field: 405 (2/2 pts)")
    else:
        print(f"✗ Wrong status for missing 'value' field: {response.status_code} (0/2 pts)")
    
    # Test 4: Invalid data type
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
    
    # Test: Non-existent string
    response = requests.get(f"{BASE_URL}/strings/nonexistent_string_123")
    if response.status_code == 404:
        get_specific_score += 5
        print("✓ Returns 404 for non-existent string (5/5 pts)")
    else:
        print(f"✗ Returns {response.status_code} for non-existent string (expected 404) (0/5 pts)")
    
    # Test: Existing string
    response = requests.get(f"{BASE_URL}/strings/{unique_str}")
    if response.status_code == 200:
        get_specific_score += 10
        print("✓ Returns 200 for existing string (10/10 pts)")
    else:
        print(f"✗ Returns {response.status_code} for existing string (expected 200) (0/10 pts)")
    
    print(f"GET specific string score: {get_specific_score}/15")
    total_score += get_specific_score
    
    # === GET /strings with filters (25 points) ===
    print("\n=== GET /strings with filters (25 points) ===")
    filter_score = 0
    
    # Create test data
    test_strings = ["a", "madam", "hello world", "test string"]
    for s in test_strings:
        try:
            requests.post(f"{BASE_URL}/strings", json={"value": f"{s}_{uuid.uuid4().hex[:4]}"})
        except:
            pass
    
    # Test various filters
    test_filters = [
        "?is_palindrome=true",
        "?min_length=3&max_length=10", 
        "?word_count=2",
        "?contains_character=a",
        "?is_palindrome=true&min_length=1"
    ]
    
    for i, filter_str in enumerate(test_filters):
        response = requests.get(f"{BASE_URL}/strings{filter_str}")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'filters_applied' in data:
                filter_score += 5
                print(f"✓ Filter test {i+1} passed (5/5 pts)")
            else:
                print(f"✗ Filter test {i+1} failed - missing response fields (0/5 pts)")
        else:
            print(f"✗ Filter test {i+1} failed - status {response.status_code} (0/5 pts)")
    
    print(f"GET with filters score: {filter_score}/25")
    total_score += filter_score
    
    # === GET /strings/filter-by-natural-language (20 points) ===
    print("\n=== GET /strings/filter-by-natural-language (20 points) ===")
    nl_score = 0
    
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
            if 'data' in data and 'interpreted_query' in data:
                nl_score += 5
                print(f"✓ Natural language query: '{query}' (5/5 pts)")
            else:
                print(f"✗ Natural language query: '{query}' - missing fields (0/5 pts)")
        else:
            print(f"✗ Natural language query: '{query}' - status {response.status_code} (0/5 pts)")
    
    print(f"Natural language filter score: {nl_score}/20")
    total_score += nl_score
    
    # === DELETE /strings/{string_value} (15 points) ===
    print("\n=== DELETE /strings/{string_value} (15 points) ===")
    delete_score = 0
    
    # Create string to delete
    delete_str = f"delete_test_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/strings", json={"value": delete_str})
    
    # Test delete existing
    response = requests.delete(f"{BASE_URL}/strings/{delete_str}")
    if response.status_code == 204:
        delete_score += 10
        print("✓ DELETE existing string (10/10 pts)")
    else:
        print(f"✗ DELETE existing string - status {response.status_code} (0/10 pts)")
    
    # Test delete non-existent
    response = requests.delete(f"{BASE_URL}/strings/nonexistent_delete")
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

if __name__ == "__main__":
    run_tests()