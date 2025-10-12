#!/usr/bin/env python3
"""
Debug des erreurs API
"""

import requests
import json

def test_api_endpoints():
    """Test les endpoints API pour identifier les problèmes"""
    base_url = "http://localhost:8080"

    print("🔍 TEST DES ENDPOINTS API")
    print("=" * 40)

    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Health check error: {e}")

    # Test 2: Courses list
    try:
        response = requests.get(f"{base_url}/api/courses")
        print(f"Courses list: {response.status_code}")
        if response.status_code == 200:
            courses = response.json()
            print(f"  Courses: {len(courses)} found")
            if courses:
                print(f"  First course: {courses[0]['id']}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Courses list error: {e}")

    # Test 3: Exercises list
    try:
        response = requests.get(f"{base_url}/api/courses/python-basics/exercises")
        print(f"Exercises list: {response.status_code}")
        if response.status_code == 200:
            exercises = response.json()
            print(f"  Exercises: {len(exercises)} found")
            if exercises:
                print(f"  First exercise: {exercises[0]['id']}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Exercises list error: {e}")

    # Test 4: Simple run
    try:
        payload = {
            "course_id": "python-basics",
            "exercise_id": "01-print",
            "code": "print('Hello World')",
            "learner": "TestUser"
        }
        response = requests.post(
            f"{base_url}/api/run",
            json=payload
        )
        print(f"Simple run: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Simple run error: {e}")

    # Test 5: Security validation
    try:
        payload = {
            "code": "print('Hello')"
        }
        response = requests.post(
            f"{base_url}/api/security/validate",
            json=payload
        )
        print(f"Security validation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Safe: {result.get('safe')}")
            print(f"  Risk level: {result.get('risk_level')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Security validation error: {e}")

if __name__ == "__main__":
    test_api_endpoints()