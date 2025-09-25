import requests
import json

# Test authentication endpoints
BASE_URL = "http://127.0.0.1:5000"

def test_signup():
    """Test user signup"""
    print("Testing signup...")
    
    signup_data = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Signup Status: {response.status_code}")
    print(f"Signup Response: {response.json()}")
    
    return response.json() if response.status_code == 201 else None

def test_login():
    """Test user login"""
    print("\nTesting login...")
    
    login_data = {
        "email": "testuser@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    print(f"Login Response: {response.json()}")
    
    return response.json() if response.status_code == 200 else None

def test_login_invalid():
    """Test login with invalid credentials"""
    print("\nTesting login with invalid credentials...")
    
    login_data = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Invalid Login Status: {response.status_code}")
    print(f"Invalid Login Response: {response.json()}")

if __name__ == "__main__":
    print("Starting authentication tests...")
    print("Make sure your Flask server is running on http://127.0.0.1:5000")
    print("=" * 50)
    
    try:
        # Test signup
        signup_result = test_signup()
        
        # Test login
        login_result = test_login()
        
        # Test invalid login
        test_login_invalid()
        
        print("\n" + "=" * 50)
        print("Authentication tests completed!")
        
        if signup_result and login_result:
            print("✅ All tests passed!")
            print(f"Token received: {login_result.get('token', 'N/A')[:50]}...")
        else:
            print("❌ Some tests failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("Make sure your Flask server is running:")
        print("cd backend && python app.py")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
