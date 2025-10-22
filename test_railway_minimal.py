import requests
import uuid

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def test_minimal():
    """Test ONLY the endpoints that failed in the bot's previous test"""
    print("🔍 TESTING PREVIOUS FAILURE POINTS")
    print("=" * 50)
    
    # The bot reported 405 errors on POST endpoints
    print("1. Testing POST endpoints (previously 405 errors):")
    
    test_string = f"minimal_test_{uuid.uuid4().hex[:8]}"
    
    # POST /strings - should return 201
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    print(f"   POST /strings (new): {response.status_code} - {'✅' if response.status_code == 201 else '❌'}")
    
    # POST /strings duplicate - should return 409  
    response = requests.post(f"{BASE_URL}/strings", json={"value": test_string})
    print(f"   POST /strings (duplicate): {response.status_code} - {'✅' if response.status_code == 409 else '❌'}")
    
    # POST with missing value - should return 400
    response = requests.post(f"{BASE_URL}/strings", json={"wrong": "field"})
    print(f"   POST missing value: {response.status_code} - {'✅' if response.status_code == 400 else '❌'}")
    
    # POST with invalid type - should return 422
    response = requests.post(f"{BASE_URL}/strings", json={"value": 123})
    print(f"   POST invalid type: {response.status_code} - {'✅' if response.status_code == 422 else '❌'}")
    
    print("\n2. Testing GET /strings with filters (previously 0 points):")
    response = requests.get(f"{BASE_URL}/strings?is_palindrome=true")
    print(f"   GET with filters: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
    
    print("\n3. Testing Natural Language (previously 0 points):")
    response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query=test")
    print(f"   Natural language: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
    
    print("\n🎯 If all above show ✅, your previous failures are FIXED!")

if __name__ == "__main__":
    test_minimal()