import requests
import sys

BASE_URL = "http://localhost:8000"

def debug_natural_language():
    print("=== Natural Language Filter Debug ===")
    
    # Test if endpoint exists
    test_url = f"{BASE_URL}/strings/filter-by-natural-language"
    print(f"Testing URL: {test_url}")
    
    # Test without query parameter
    response = requests.get(test_url)
    print(f"Without query param: {response.status_code}")
    if response.status_code != 400:
        print(f"Expected 400 for missing query, got {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test with query parameter
    test_queries = [
        "all single word palindromic strings",
        "strings longer than 5 characters",
        "test"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        response = requests.get(f"{test_url}?query={query}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            if 'interpreted_query' in data:
                print(f"Interpreted: {data['interpreted_query']}")
        else:
            print(f"Error: {response.text}")
    
    # Check server logs for any Python errors
    print("\n🔍 Check your Django server console for any Python errors!")

if __name__ == "__main__":
    debug_natural_language()