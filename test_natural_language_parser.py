import requests
import json

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

def test_natural_language_queries():
    """Test specific natural language queries mentioned in the task"""
    
    test_queries = [
        "all single word palindromic strings",
        "strings longer than 10 characters", 
        "palindromic strings that contain the first vowel",
        "strings containing the letter z",
        "all strings with two words",
        "palindromic strings longer than 5 characters",
        "strings containing the letter a",
        "single word strings"
    ]
    
    print("🧪 TESTING NATURAL LANGUAGE PARSER")
    print("=" * 60)
    
    # First, create some test data
    test_strings = [
        "racecar",           # palindrome, 1 word, contains 'a', length 7
        "hello",             # 1 word, contains 'e', length 5  
        "hello world",       # 2 words, contains 'o', length 11
        "madam",             # palindrome, 1 word, contains 'a', length 5
        "python programming", # 2 words, contains 'o', length 18
        "a",                 # palindrome, 1 word, contains 'a', length 1
        "test string here",  # 3 words, contains 'e', length 15
    ]
    
    print("Creating test data...")
    for string in test_strings:
        try:
            response = requests.post(f"{BASE_URL}/strings", json={"value": string}, timeout=10)
            if response.status_code == 201:
                print(f"  ✅ Created: '{string}'")
            elif response.status_code == 409:
                print(f"  ⚠️  Already exists: '{string}'")
            else:
                print(f"  ❌ Failed to create '{string}': {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error creating '{string}': {e}")
    
    print("\n" + "=" * 60)
    print("TESTING NATURAL LANGUAGE QUERIES")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 50)
        
        try:
            response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                interpreted = data['interpreted_query']
                parsed_filters = interpreted['parsed_filters']
                
                print(f"  ✅ Status: 200")
                print(f"  📊 Results: {data['count']} strings found")
                print(f"  🎯 Parsed filters: {parsed_filters}")
                
                # Show a few results
                if data['count'] > 0:
                    print(f"  📝 Sample results:")
                    for i, item in enumerate(data['data'][:3]):  # Show first 3
                        print(f"     {i+1}. '{item['value']}' (words: {item['properties']['word_count']}, "
                              f"palindrome: {item['properties']['is_palindrome']}, "
                              f"length: {item['properties']['length']})")
                else:
                    print("  ❌ No results found - check if filters are too strict")
                    
            else:
                print(f"  ❌ Status: {response.status_code}")
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")

def test_specific_cases():
    """Test the exact cases mentioned in the bot feedback"""
    print("\n" + "=" * 60)
    print("TESTING BOT-SPECIFIC CASES")
    print("=" * 60)
    
    bot_cases = [
        "all single word palindromic strings",  # Should return word_count=1, is_palindrome=true
        "strings longer than 5 characters",     # Should return min_length=6
        "palindromic strings that contain the letter a",  # Should return is_palindrome=true, contains_character='a'
        "strings containing the letter e"       # Should return contains_character='e'
    ]
    
    for query in bot_cases:
        print(f"\n🎯 Bot Case: '{query}'")
        response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language?query={query}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: 200")
            print(f"  📊 Results: {data['count']} strings")
            print(f"  🎯 Parsed: {data['interpreted_query']['parsed_filters']}")
        else:
            print(f"  ❌ Status: {response.status_code}")

if __name__ == "__main__":
    test_natural_language_queries()
    test_specific_cases()