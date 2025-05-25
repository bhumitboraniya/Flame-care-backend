#!/usr/bin/env python3
"""
Test script for the FlameCare Burn Fluid Calculator API
"""

import requests
import json

# API base URL (adjust if needed)
BASE_URL = "http://localhost:5001"

def test_fluid_calculator_api():
    """Test the fluid calculator API endpoint"""
    print("🔥 Testing FlameCare Burn Fluid Calculator API 🔥")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Standard Adult Burn",
            "data": {
                "weight_kg": 70,
                "tbsa_percentage": 25,
                "delayed_hours": 0,
                "is_adult": True
            }
        },
        {
            "name": "Pediatric Burn",
            "data": {
                "weight_kg": 30,
                "tbsa_percentage": 20,
                "delayed_hours": 0,
                "is_adult": False
            }
        },
        {
            "name": "Major Burn with Delay",
            "data": {
                "weight_kg": 80,
                "tbsa_percentage": 45,
                "delayed_hours": 3,
                "is_adult": True
            }
        },
        {
            "name": "Minor Burn",
            "data": {
                "weight_kg": 65,
                "tbsa_percentage": 10,
                "delayed_hours": 0,
                "is_adult": True
            }
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Input: {test_case['data']}")
        
        try:
            # Make API request
            response = requests.post(
                f"{BASE_URL}/api/calculate-fluid",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                fluid_req = result['fluid_requirements']
                
                print(f"✅ Success!")
                print(f"   Total fluid: {fluid_req['total_ml']} ml")
                print(f"   First 8h: {fluid_req['first_8h_ml']} ml ({fluid_req['first_8h_rate']} ml/hr)")
                print(f"   Next 16h: {fluid_req['next_16h_ml']} ml ({fluid_req['next_16h_rate']} ml/hr)")
                print(f"   Severity: {result['patient_info']['burn_severity']}")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            print("   Make sure the Flask server is running on port 5001")
        
        print("-" * 40)

def test_health_check():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Server is running: {result['message']}")
            print("Available endpoints:")
            for endpoint, description in result['endpoints'].items():
                print(f"   {endpoint}: {description}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")

def test_sample_endpoint():
    """Test the sample test endpoint"""
    print("\n🧪 Testing Sample Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/test-fluid", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sample tests completed")
            for test in result['test_results']:
                print(f"   {test['description']}: {test['result']['total_ml']} ml total")
        else:
            print(f"❌ Sample test failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")

if __name__ == "__main__":
    print("Starting API tests...")
    
    # Test health check first
    test_health_check()
    
    # Test sample endpoint
    test_sample_endpoint()
    
    # Test fluid calculator
    test_fluid_calculator_api()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("If you see connection errors, start the Flask server with:")
    print("cd FlameCareBackend && python app.py")
