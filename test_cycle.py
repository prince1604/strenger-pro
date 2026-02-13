import httpx
import time

BASE_URL = "http://127.0.0.1:8000"

def test_full_cycle():
    email = f"test_{int(time.time())}@example.com"
    username = f"user_{int(time.time())}"
    password = "password123"
    
    print(f"--- Testing Full Cycle with {email} ---")
    
    with httpx.Client() as client:
        # 1. Register
        reg_data = {
            "username": username,
            "email": email,
            "password": password,
            "gender": "male",
            "avatar_type": "boy"
        }
        r = client.post(f"{BASE_URL}/register", json=reg_data)
        print(f"Register Status: {r.status_code}")
        print(f"Register Resp: {r.text}")
        
        if r.status_code != 200:
            print("Registration Failed!")
            return

        # 2. Login
        login_data = {"email": email, "password": password}
        r = client.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login Status: {r.status_code}")
        print(f"Login Resp: {r.text}")
        
        if r.status_code == 200:
            print("SUCCESS: Registration and Login are PERFECT.")
        else:
            print("FAILURE: Login failed after successful registration.")

if __name__ == "__main__":
    test_full_cycle()
