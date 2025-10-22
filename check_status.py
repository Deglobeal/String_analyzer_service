import requests

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def quick_status():
    """Quick check of all critical endpoints"""
    print("🚀 QUICK STATUS CHECK")
    print("=" * 50)
    
    endpoints = [
        ("POST /strings", f"{BASE_URL}/strings", "POST"),
        ("GET /strings/{value}", f"{BASE_URL}/strings/test", "GET"),
        ("GET /strings?filters", f"{BASE_URL}/strings?is_palindrome=true", "GET"),
        ("GET /natural-language", f"{BASE_URL}/strings/filter-by-natural-language?query=test", "GET"),
        ("DELETE /strings/{value}", f"{BASE_URL}/strings/test", "DELETE")
    ]
    
    print("Endpoint Status:")
    print("-" * 50)
    
    all_working = True
    
    for name, url, method in endpoints:
        try:
            if method == "POST":
                response = requests.post(url, json={"value": "test"})
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                response = requests.get(url)
            
            # Check if it's NOT 405 (Method Not Allowed)
            if response.status_code != 405:
                print(f"✅ {name}: {response.status_code}")
            else:
                print(f"❌ {name}: 405 Method Not Allowed")
                all_working = False
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_working = False
    
    print("\n" + "=" * 50)
    if all_working:
        print("🎯 ALL ENDPOINTS ARE ACCESSIBLE!")
        print("🚀 Ready for bot submission!")
    else:
        print("⚠️ Some endpoints have issues.")
        print("   Fix the 405 errors before submitting.")

if __name__ == "__main__":
    quick_status()