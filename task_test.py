#!/usr/bin/env python3
"""
task_test.py

Run this while your Django server is running. It performs the same checks
the Stage-1 autograder uses and prints a scored report.

Usage:
    python task_test.py
Or set BASE_URL env var:
    BASE_URL="http://127.0.0.1:8000" python task_test.py
"""

import os
import sys
import hashlib
import urllib.parse
import requests
import json
from typing import Optional

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/")

def full(path: str) -> str:
    return BASE_URL + path

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def post_json(path: str, body):
    try:
        return requests.post(full(path), json=body, timeout=5)
    except Exception as e:
        print("Request error:", e)
        return None

def get(path: str, params=None):
    try:
        return requests.get(full(path), params=params, timeout=5)
    except Exception as e:
        print("Request error:", e)
        return None

def delete(path: str):
    try:
        return requests.delete(full(path), timeout=5)
    except Exception as e:
        print("Request error:", e)
        return None

def parse_response_json(r):
    try:
        return r.json()
    except Exception:
        return None

def ok(msg):
    print("✓", msg)

def fail(msg):
    print("✗", msg)

def run():
    sections = {
        "post": 25,
        "get_specific": 15,
        "get_filters": 25,
        "get_nl": 20,
        "delete": 15
    }

    total = 0
    print("\n============================================================")
    print("Running Stage-1 verification against:", BASE_URL)
    print("============================================================\n")

    # === POST /strings ===
    post_score = 0
    print("=== POST /strings (25 points) ===")
    v = "task_test_unique_string_12345"
    # create new
    r = post_json("/strings", {"value": v})
    if r is None:
        fail("No response for POST /strings - is the server running?")
    else:
        if r.status_code == 201:
            ok("status code: 201 (create)")
            post_score += 5
        else:
            fail(f"Wrong status code: {r.status_code} (expected 201)")

    # duplicate -> expect 409
    r2 = post_json("/strings", {"value": v})
    if r2 is not None and r2.status_code == 409:
        ok("status for duplicate: 409")
        post_score += 5
    else:
        if r2 is None:
            fail("No response for duplicate POST /strings")
        else:
            fail(f"Wrong status for duplicate: {r2.status_code} (expected 409)")

    # missing 'value' -> expect 400
    r3 = post_json("/strings", {})
    if r3 is not None and r3.status_code == 400:
        ok("status for missing 'value' field: 400")
        post_score += 2
    else:
        if r3 is None:
            fail("No response for POST /strings with empty body")
        else:
            fail(f"Wrong status for missing 'value' field: {r3.status_code} (expected 400)")

    # invalid data type -> expect 422 (spec mandates 422 for wrong type)
    r4 = post_json("/strings", {"value": 12345})
    if r4 is not None and r4.status_code in (422,):
        ok("status for invalid data type: 422")
        post_score += 3
    else:
        if r4 is None:
            fail("No response for POST /strings with invalid type")
        else:
            fail(f"Wrong status for invalid data type: {r4.status_code} (expected 422)")

    print(f"POST /strings score: {post_score}/{sections['post']}\n")
    total += post_score

    # === GET /strings/{string_value} ===
    get_spec_score = 0
    print("=== GET /strings/{string_value} (15 points) ===")
    # 404 for non-existent
    r = get("/strings/nonexistent_task_test_value")
    if r is not None and r.status_code == 404:
        ok("Returns 404 for non-existent string")
        get_spec_score += 5
    else:
        if r is None:
            fail("No response for GET nonexistent")
        else:
            fail(f"GET nonexistent returned {r.status_code} (expected 404)")

    # GET existing
    encoded = urllib.parse.quote(v, safe='')
    r = get(f"/strings/{encoded}")
    if r is not None and r.status_code == 200:
        ok("Returns 200 for existing string")
        get_spec_score += 10
        # optional: verify body contains value and properties
        data = parse_response_json(r)
        if data is None:
            fail("GET existing returned non-JSON body")
        else:
            # pass
            pass
    else:
        if r is None:
            fail("No response for GET existing")
        else:
            fail(f"GET existing returned {r.status_code} (expected 200)")

    print(f"GET specific string score: {get_spec_score}/{sections['get_specific']}\n")
    total += get_spec_score

    # === GET /strings with filters ===
    filter_score = 0
    print("=== GET /strings with filters (25 points) ===")
    # Add sample strings
    samples = [
        "racecar",  # palindrome, single word
        "hello world",  # two words
        "abcdefghijklmnop",  # long
        "aa bb",  # two words
        "pal a lap"  # contains a and spaces
    ]
    for s in samples:
        try:
            post_json("/strings", {"value": s})
        except:
            pass

    # Helper to extract list from response
    def extract_list(resp):
        if resp is None:
            return None
        try:
            j = resp.json()
        except:
            return None
        if isinstance(j, dict) and "data" in j:
            return j["data"]
        if isinstance(j, list):
            return j
        # fallback: maybe top-level object is one item
        return [j]

    # 1) is_palindrome=true
    r = get("/strings", params={"is_palindrome": "true"})
    arr = extract_list(r)
    if r is not None and r.status_code == 200 and arr is not None:
        ok_flag = True
        for item in arr:
            # item may have properties or top-level flags
            p = None
            if isinstance(item, dict):
                if "properties" in item and isinstance(item["properties"], dict):
                    p = item["properties"].get("is_palindrome")
                else:
                    p = item.get("is_palindrome")
            if p not in (True, "true", 1, "1"):
                ok_flag = False
                break
        if ok_flag:
            ok("Filter test 1 (is_palindrome=true) passed")
            filter_score += 5
        else:
            fail("Filter test 1 returned non-palindrome items")
    else:
        fail(f"Filter test 1 HTTP {None if r is None else r.status_code}")

    # 2) min_length=5 & max_length=20
    r = get("/strings", params={"min_length": "5", "max_length": "20"})
    arr = extract_list(r)
    if r is not None and r.status_code == 200 and arr is not None:
        ok_flag = True
        for item in arr:
            length = None
            if isinstance(item, dict):
                if "properties" in item and isinstance(item["properties"], dict):
                    length = item["properties"].get("length")
                else:
                    length = item.get("length")
            if length is None:
                ok_flag = False
                break
            try:
                if not (5 <= int(length) <= 20):
                    ok_flag = False
                    break
            except:
                ok_flag = False
                break
        if ok_flag:
            ok("Filter test 2 (min_length & max_length) passed")
            filter_score += 5
        else:
            fail("Filter test 2 returned items outside length range or missing length")
    else:
        fail(f"Filter test 2 HTTP {None if r is None else r.status_code}")

    # 3) word_count=1
    r = get("/strings", params={"word_count": "1"})
    arr = extract_list(r)
    if r is not None and r.status_code == 200 and arr is not None:
        ok_flag = True
        for item in arr:
            wc = None
            if isinstance(item, dict):
                if "properties" in item and isinstance(item["properties"], dict):
                    wc = item["properties"].get("word_count")
                else:
                    wc = item.get("word_count")
            if wc is None:
                ok_flag = False
                break
            try:
                if int(wc) != 1:
                    ok_flag = False
                    break
            except:
                ok_flag = False
                break
        if ok_flag:
            ok("Filter test 3 (word_count=1) passed")
            filter_score += 5
        else:
            fail("Filter test 3 returned items not matching word_count=1")
    else:
        fail(f"Filter test 3 HTTP {None if r is None else r.status_code}")

    # 4) contains_character=a
    r = get("/strings", params={"contains_character": "a"})
    arr = extract_list(r)
    if r is not None and r.status_code == 200 and arr is not None:
        ok_flag = True
        for item in arr:
            v = ""
            if isinstance(item, dict):
                v = item.get("value") or (item.get("properties") or {}).get("value") or ""
            if 'a' not in (v or "").lower():
                ok_flag = False
                break
        if ok_flag:
            ok("Filter test 4 (contains_character=a) passed")
            filter_score += 5
        else:
            fail("Filter test 4 returned items not containing 'a'")
    else:
        fail(f"Filter test 4 HTTP {None if r is None else r.status_code}")

    # 5) combined: is_palindrome=true & word_count=1
    r = get("/strings", params={"is_palindrome": "true", "word_count": "1"})
    arr = extract_list(r)
    if r is not None and r.status_code == 200 and arr is not None:
        ok_flag = True
        for item in arr:
            p = None; wc = None
            if isinstance(item, dict):
                props = item.get("properties", {})
                if props:
                    p = props.get("is_palindrome")
                    wc = props.get("word_count")
                else:
                    p = item.get("is_palindrome")
                    wc = item.get("word_count")
            if p not in (True, "true", 1, "1"):
                ok_flag = False
                break
            try:
                if int(wc) != 1:
                    ok_flag = False
                    break
            except:
                ok_flag = False
                break
        if ok_flag:
            ok("Filter test 5 (is_palindrome=true & word_count=1) passed")
            filter_score += 5
        else:
            fail("Filter test 5 returned items not matching both filters")
    else:
        fail(f"Filter test 5 HTTP {None if r is None else r.status_code}")

    print(f"GET with filters score: {filter_score}/{sections['get_filters']}\n")
    total += filter_score

    # === GET /strings/filter-by-natural-language ===
    nl_score = 0
    print("=== GET /strings/filter-by-natural-language (20 points) ===")
    nl_tests = [
        ("all single word palindromic strings", {"word_count":1, "is_palindrome":True}),
        ("strings longer than 5 characters", {"min_length":6}),
        ("palindromic strings that contain the letter a", {"is_palindrome":True, "contains_character":"a"}),
        ("strings containing the letter e", {"contains_character":"e"})
    ]

    for text, expected in nl_tests:
        r = get("/strings/filter-by-natural-language", params={"q": text})
        if r is None:
            fail(f"Natural language query: '{text}' - no response")
            continue
        if r.status_code != 200:
            fail(f"Natural language query: '{text}' - status {r.status_code}")
            continue
        j = parse_response_json(r)
        if j is None:
            fail(f"Natural language query: '{text}' - invalid JSON")
            continue

        # Preferred format: dict with 'data' and 'interpreted_query' and parsed_filters
        passed = False
        if isinstance(j, dict) and "interpreted_query" in j and isinstance(j["interpreted_query"], dict):
            parsed = j["interpreted_query"].get("parsed_filters", {})
            # check expected keys appear
            ok_flag = True
            for k, v in expected.items():
                if k not in parsed:
                    ok_flag = False
                    break
            if ok_flag:
                ok(f"Natural language query: '{text}' passed (parsed filters present)")
                nl_score += 5
                passed = True

        if not passed:
            # If server returns list of results only, do heuristic check on returned items
            arr = j if isinstance(j, list) else j.get("data", [])
            if not isinstance(arr, list):
                fail(f"Natural language query: '{text}' - unexpected response shape")
                continue
            if len(arr) == 0:
                # No matched items — autograder expects parsed filters ideally; mark fail
                fail(f"Natural language query: '{text}' returned 200 but no data")
            else:
                # quick heuristic: check at least one item satisfies one expected predicate
                ok_item = False
                for item in arr:
                    if not isinstance(item, dict):
                        continue
                    val = item.get("value") or (item.get("properties") or {}).get("value") or ""
                    if expected.get("contains_character") and expected["contains_character"] in val.lower():
                        ok_item = True
                        break
                    if expected.get("is_palindrome") and val and val.lower() == val.lower()[::-1]:
                        ok_item = True
                        break
                    if expected.get("min_length") and val and len(val) >= expected["min_length"]:
                        ok_item = True
                        break
                if ok_item:
                    ok(f"Natural language query: '{text}' returned matching items (no parsed metadata)")
                    nl_score += 5
                else:
                    fail(f"Natural language query: '{text}' returned items but none match expectations")

    print(f"Natural language filter score: {nl_score}/{sections['get_nl']}\n")
    total += nl_score

    # === DELETE /strings/{string_value} ===
    del_score = 0
    print("=== DELETE /strings/{string_value} (15 points) ===")
    r = delete(f"/strings/{urllib.parse.quote(v, safe='')}")
    if r is not None and r.status_code == 204:
        ok("DELETE existing string")
        del_score += 10
    else:
        fail(f"DELETE existing returned {None if r is None else r.status_code} (expected 204)")

    r = delete("/strings/nonexistent_delete_abc123")
    if r is not None and r.status_code == 404:
        ok("DELETE non-existent string")
        del_score += 5
    else:
        fail(f"DELETE non-existent returned {None if r is None else r.status_code} (expected 404)")

    print(f"DELETE string score: {del_score}/{sections['delete']}\n")
    total += del_score

    print("=== Cleanup ===")
    print("============================================================")
    print(f"FINAL SCORE: {total}/100")
    print("============================================================\n")

    # exit non-zero if not perfect so CI / graders can detect failure
    if total < 100:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run()
