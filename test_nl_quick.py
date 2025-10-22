import requests

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def quick_test():
    """Quick test to verify natural language parsing is working"""
    print("🚀 QUICK NATURAL LANGUAGE TEST")
    print("=" * 50)
    
    test_cases = [
        ("all single word palindromic strings", "Should return word_count=1, is_palindrome=true"),
        ("strings longer than 5 characters", "Should return min_length=6"),
        ("palindromic strings that contain the letter a", "Should return is_palindrome=true, contains_character='a'"),
        ("strings containing the letter e", "Should return contains_character='e'")
    ]
    
    for query, expected in test_cases:
        print(f"\n🔍 Testing: '{query}'")
        print(f"   Expected: {expected}")
        
        response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            filters = data['interpreted_query']['parsed_filters']
            count = data['count']
            
            print(f"   ✅ Status: 200")
            print(f"   🎯 Parsed filters: {filters}")
            print(f"   📊 Results found: {count}")
            
            # Check if we got the expected filters
            if "single word palindromic" in query:
                if filters.get('word_count') == 1 and filters.get('is_palindrome') == True:
                    print("   ✅ CORRECT: word_count=1 and is_palindrome=true detected")
                else:
                    print("   ❌ INCORRECT: Expected word_count=1 and is_palindrome=true")
            
            elif "longer than 5" in query:
                if filters.get('min_length') == 6:
                    print("   ✅ CORRECT: min_length=6 detected")
                else:
                    print("   ❌ INCORRECT: Expected min_length=6")
            
            elif "contain the letter a" in query:
                if filters.get('is_palindrome') == True and filters.get('contains_character') == 'a':
                    print("   ✅ CORRECT: is_palindrome=true and contains_character='a' detected")
                else:
                    print("   ❌ INCORRECT: Expected is_palindrome=true and contains_character='a'")
            
            elif "containing the letter e" in query:
                if filters.get('contains_character') == 'e':
                    print("   ✅ CORRECT: contains_character='e' detected")
                else:
                    print("   ❌ INCORRECT: Expected contains_character='e'")
                    
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")

if __name__ == "__main__":
    quick_test()