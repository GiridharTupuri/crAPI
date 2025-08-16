"""
Simple Locust test to debug authentication issues
"""

import json
import random
import string
from locust import HttpUser, task, between


class SimpleUser(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        """Test basic authentication"""
        print("Starting simple user test...")
        
        random_string = ''.join(random.choices(string.ascii_lowercase, k=6))
        user_data = {
            "name": f"TestUser{random_string}",
            "email": f"test{random_string}@example.com",
            "number": f"555{random.randint(1000000, 9999999)}",
            "password": f"TestPass{random_string}123!"
        }
        
        print(f"Attempting signup with email: {user_data['email']}")
        
        signup_response = self.client.post(
            "/identity/api/auth/signup",
            json=user_data,
            headers={"Content-Type": "application/json"},
            name="Simple: Signup"
        )
        
        print(f"Signup response: {signup_response.status_code}")
        if signup_response.status_code != 200:
            print(f"Signup failed: {signup_response.text}")
            return
        
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = self.client.post(
            "/identity/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            name="Simple: Login"
        )
        
        print(f"Login response: {login_response.status_code}")
        if login_response.status_code == 200:
            response_data = login_response.json()
            self.token = response_data.get("token")
            print(f"Token received: {bool(self.token)}")
        else:
            print(f"Login failed: {login_response.text}")
    
    @task
    def test_homepage(self):
        """Test simple homepage access"""
        self.client.get("/", name="Simple: Homepage")
    
    @task
    def test_dashboard(self):
        """Test dashboard if we have a token"""
        if hasattr(self, 'token') and self.token:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            self.client.get(
                "/identity/api/v2/user/dashboard",
                headers=headers,
                name="Simple: Dashboard"
            )
