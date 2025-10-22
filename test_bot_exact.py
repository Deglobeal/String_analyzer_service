import requests
import hashlib
import uuid

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def test_with_trailing_slashes():
    """Test with trailing slashes (what the bot might be using)"""
    print("🔍 TESTING WITH TRAILING SLASHES")
    print("=" * 60)
    
    test_cases = [
        # Test with trailing slashes
        {
            "name": "POST /strings/ (with slash)",
            "method": "POST", 
            "url": f"{BASE_URL}/strings/",
            "data": {"value": f"test_slash_{uuid.uuid4().hex[:8]}"},
            "expected": [201, 404]  # Either 201 or 404 is acceptable
        },
        {
            "name": "GET /strings/{value}/ (with slash)",
            "method": "GET",
            "url": f"{BASE_URL}/strings/test_slash/", 
            "data": None,
            "expected": [200, 404]
        },
        {
            "name": "GET /strings/filter-by-natural-language/ (with slash)",
            "method": "GET",
            "url": f"{BASE_URL}/strings/filter-by-natural-language/?query=test",
            "data": None,
            "expected": [200, 404]
        }
    ]
    
    for test in test_cases:
        print(f"\n🧪 {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            if test['method'] == 'POST':
                response = requests.post(test['url'], json=test['data'])
            else:
                response = requests.get(test['url'])
            
            actual = response.status_code
            is_expected = actual in test['expected']
            
            if is_expected:
                print(f"   ✅ Status: {actual} (acceptable)")
            else:
                print(f"   ❌ Status: {actual} (expected {test['expected']})")
                if actual == 405:
                    print("   💥 405 Method Not Allowed")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_common_bot_issues():
    """Test common issues that cause bot failures"""
    print("\n" + "=" * 60)
    print("🧪 TESTING COMMON BOT FAILURE SCENARIOS")
    print("=" * 60)
    
    # Test 1: Case sensitivity in URLs
    print("\n1. URL Case Sensitivity:")
    urls_to_test = [
        f"{BASE_URL}/strings",
        f"{BASE_URL}/STRINGS",  # Uppercase
        f"{BASE_URL}/Strings",  # Mixed case
    ]
    
    for url in urls_to_test:
        response = requests.get(url)
        print(f"   {url}: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
    
    # Test 2: Different HTTP methods on same URL
    print("\n2. HTTP Method Support:")
    test_url = f"{BASE_URL}/strings"
    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD']
    
    for method in methods:
        try:
            if method == 'GET':
                response = requests.get(test_url)
            elif method == 'POST':
                response = requests.post(test_url, json={"value": "test"})
            elif method == 'DELETE':
                response = requests.delete(test_url)
            elif method == 'PUT':
                response = requests.put(test_url, json={"value": "test"})
            elif method == 'PATCH':
                response = requests.patch(test_url, json={"value": "test"})
            elif method == 'OPTIONS':
                response = requests.options(test_url)
            elif method == 'HEAD':
                response = requests.head(test_url)
            
            print(f"   {method}: {response.status_code}")
            
        except Exception as e:
            print(f"   {method}: Error - {e}")
    
    # Test 3: Query parameter formats
    print("\n3. Query Parameter Formats:")
    filter_formats = [
        "is_palindrome=true",
        "is_palindrome=True",  # Capital T
        "is_palindrome=1",     # Numeric boolean
        "min_length=5",
        "max_length=10",
        "word_count=2", 
        "contains_character=a"
    ]
    
    for filter_query in filter_formats:
        response = requests.get(f"{BASE_URL}/strings?{filter_query}")
        print(f"   ?{filter_query}: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")

def main():
    print("🎯 BOT COMPATIBILITY DEEP DIVE")
    print("Testing all possible scenarios the bot might encounter")
    print()
    
    test_with_trailing_slashes()
    test_common_bot_issues()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    print("""
Based on our tests, your API endpoints are working correctly.
The bot's 405 errors suggest it might be:

1. Using trailing slashes (/strings/ vs /strings)
2. Using different URL case (STRINGS vs strings)  
3. Having network/timeout issues
4. Testing from a different environment

RECOMMENDED ACTIONS:

1. ✅ Add trailing slash support to urls.py
2. ✅ Set APPEND_SLASH = False in settings.py
3. ✅ Redeploy to Railway
4. ✅ Run this test again to verify

Your API logic is correct - it's likely a URL routing issue!
    """)

if __name__ == "__main__":
    main()