import requests

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    endpoints = [
        "/strings",
        "/strings-list", 
        "/strings/filter-by-natural-language?query=test",
        "/strings/delete/test123"
    ]
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        try:
            if endpoint == "/strings":
                # Test POST for /strings
                response = requests.post(url, json={"value": f"debug test"})
                method = "POST"
            elif "delete" in endpoint:
                # Test DELETE
                response = requests.delete(url)
                method = "DELETE"
            else:
                # Test GET for others
                response = requests.get(url)
                method = "GET"
                
            print(f"{method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint}: {e}")

if __name__ == "__main__":
    test_all_endpoints()