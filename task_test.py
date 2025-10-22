import requests
import hashlib
import uuid
import json

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def test_bot_exact_scenarios():
    """
    Test the EXACT scenarios that the bot is testing
    Based on the bot's failure report
    """
    print("🔍 DIAGNOSING BOT 405 ERRORS")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")
    print()
    
    # The bot reported 405 errors on ALL POST endpoints
    # This means the URL routing is broken
    
    test_cases = [
        # POST scenarios that got 405
        {
            "name": "POST /strings (new)",
            "method": "POST",
            "url": f"{BASE_URL}/strings",
            "data": {"value": f"test_{uuid.uuid4().hex[:8]}"},
            "expected": 201
        },
        {
            "name": "POST /strings (duplicate)", 
            "method": "POST",
            "url": f"{BASE_URL}/strings",
            "data": {"value": "duplicate_test"},
            "expected": 409
        },
        {
            "name": "POST /strings (missing value)",
            "method": "POST", 
            "url": f"{BASE_URL}/strings",
            "data": {"wrong_field": "test"},
            "expected": 400
        },
        {
            "name": "POST /strings (invalid type)",
            "method": "POST",
            "url": f"{BASE_URL}/strings", 
            "data": {"value": 123},
            "expected": 422
        },
        # GET scenarios that should work
        {
            "name": "GET /strings/{value} (non-existent)",
            "method": "GET",
            "url": f"{BASE_URL}/strings/nonexistent_123",
            "data": None,
            "expected": 404
        },
        {
            "name": "GET /strings?filters",
            "method": "GET",
            "url": f"{BASE_URL}/strings?is_palindrome=true",
            "data": None, 
            "expected": 200
        },
        {
            "name": "GET /natural-language",
            "method": "GET",
            "url": f"{BASE_URL}/strings/filter-by-natural-language?query=test",
            "data": None,
            "expected": 200
        },
        {
            "name": "DELETE /strings/{value}",
            "method": "DELETE", 
            "url": f"{BASE_URL}/strings/test_delete",
            "data": None,
            "expected": 404
        }
    ]
    
    # First create a string for duplicate test
    requests.post(f"{BASE_URL}/strings", json={"value": "duplicate_test"})
    
    results = {}
    
    for test in test_cases:
        print(f"\n🧪 {test['name']}")
        print(f"   URL: {test['url']}")
        print(f"   Method: {test['method']}")
        print(f"   Expected: {test['expected']}")
        
        try:
            if test['method'] == 'POST':
                response = requests.post(test['url'], json=test['data'])
            elif test['method'] == 'GET':
                response = requests.get(test['url'])
            elif test['method'] == 'DELETE':
                response = requests.delete(test['url'])
            
            actual = response.status_code
            results[test['name']] = actual == test['expected']
            
            if actual == test['expected']:
                print(f"   ✅ Status: {actual}")
            else:
                print(f"   ❌ Status: {actual} (expected {test['expected']})")
                if actual == 405:
                    print("   💥 CRITICAL: 405 Method Not Allowed")
                    print("      This means the URL route exists but doesn't accept this HTTP method")
                    print("      Check your URL routing in urls.py")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[test['name']] = False
    
    # Analysis
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        print(f"  {'✅' if success else '❌'} {test_name}")
    
    print(f"\n🎯 Score: {passed}/{total}")
    
    # Check for 405 pattern
    post_405_count = sum(1 for name in results if 'POST' in name and not results[name])
    if post_405_count > 0:
        print(f"\n💥 CRITICAL ISSUE: {post_405_count} POST endpoints returning 405")
        print("   This is the EXACT problem the bot reported!")
        print("   Your URL routing is broken for POST methods")

def debug_url_routing():
    """Debug the URL routing to find the issue"""
    print("\n" + "=" * 60)
    print("🔧 URL ROUTING DEBUG")
    print("=" * 60)
    
    # Test different URL patterns
    test_urls = [
        f"{BASE_URL}/strings",
        f"{BASE_URL}/strings/",
        f"{BASE_URL}/strings/test",
        f"{BASE_URL}/strings/filter-by-natural-language",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        
        # Test all methods
        methods = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']
        for method in methods:
            try:
                if method == 'GET':
                    response = requests.get(url)
                elif method == 'POST':
                    response = requests.post(url, json={"value": "test"})
                elif method == 'DELETE':
                    response = requests.delete(url)
                elif method == 'PUT':
                    response = requests.put(url, json={"value": "test"})
                elif method == 'PATCH':
                    response = requests.patch(url, json={"value": "test"})
                
                print(f"  {method}: {response.status_code}")
                
            except Exception as e:
                print(f"  {method}: Error - {e}")

def check_railway_deployment():
    """Check if the deployment has the latest code"""
    print("\n" + "=" * 60)
    print("🚀 RAILWAY DEPLOYMENT CHECK")
    print("=" * 60)
    
    # Test if we can access any endpoint
    test_endpoints = [
        "/strings",
        "/strings/test",
        "/strings/filter-by-natural-language?query=test"
    ]
    
    for endpoint in test_endpoints:
        url = BASE_URL + endpoint
        print(f"\nTesting: {url}")
        
        # Test GET
        try:
            response = requests.get(url)
            print(f"  GET: {response.status_code}")
            if response.status_code == 405:
                print("  💥 405 Method Not Allowed")
        except Exception as e:
            print(f"  GET: Error - {e}")
        
        # Test POST
        if endpoint == "/strings":
            try:
                response = requests.post(url, json={"value": "deployment_test"})
                print(f"  POST: {response.status_code}")
                if response.status_code == 405:
                    print("  💥 405 Method Not Allowed - URL ROUTING BROKEN")
            except Exception as e:
                print(f"  POST: Error - {e}")

def main():
    """Main diagnostic function"""
    print("🚨 BOT FAILURE DIAGNOSTIC TOOL")
    print("This will diagnose why the bot is getting 405 errors")
    print()
    
    # Run diagnostics
    test_bot_exact_scenarios()
    debug_url_routing() 
    check_railway_deployment()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDED FIXES")
    print("=" * 60)
    
    print("""
1. 🔥 URGENT: Fix URL Routing
   - The 405 errors mean your URLs exist but don't accept the HTTP method
   - Check your strings/urls.py and make sure you're using class-based views
   - Ensure you have:
        path('strings', views.StringsView.as_view(), name='strings'),
        path('strings/<str:string_value>', views.StringDetailView.as_view(), name='string-detail'),

2. 🚀 Redeploy to Railway
   - Make sure your latest code is deployed
   - Check Railway logs for deployment errors

3. ✅ Verify Deployment
   - Run this test again after fixes
   - All POST endpoints should return 201/409/400/422, NOT 405

4. 🔄 Test Before Resubmitting
   - Use this diagnostic tool to verify fixes
   - Only submit when ALL 405 errors are gone
    """)

if __name__ == "__main__":
    main()