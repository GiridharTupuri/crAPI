"""
Locust Performance Testing Script for crAPI Application
Comprehensive load testing covering main user workflows
"""

import json
import random
import string
from locust import HttpUser, task, between
from locust.exception import StopUser


class CRAPIUser(HttpUser):
    """
    Simulates a typical crAPI user performing various operations
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user_email = None
        self.user_password = None
        self.vehicle_id = None
        
    def on_start(self):
        """Called when a user starts - performs signup and login"""
        try:
            self.signup_and_login()
        except Exception as e:
            print(f"Authentication failed for user: {e}")
            raise StopUser()
    
    def generate_random_user_data(self):
        """Generate random user data for registration"""
        random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
        return {
            "name": f"TestUser{random_string}",
            "email": f"test{random_string}@example.com",
            "number": f"555{random.randint(1000000, 9999999)}",
            "password": f"TestPass{random_string}123!"
        }
    
    def signup_and_login(self):
        """Register a new user and login to get authentication token"""
        user_data = self.generate_random_user_data()
        self.user_email = user_data["email"]
        self.user_password = user_data["password"]
        
        signup_response = self.client.post(
            "/identity/api/auth/signup",
            json=user_data,
            headers={"Content-Type": "application/json"},
            name="Auth: Signup"
        )
        
        if signup_response.status_code != 200:
            print(f"Signup failed: {signup_response.status_code} - {signup_response.text}")
            raise StopUser()
        
        login_data = {
            "email": self.user_email,
            "password": self.user_password
        }
        
        login_response = self.client.post(
            "/identity/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            name="Auth: Login"
        )
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            self.token = response_data.get("token")
            if not self.token:
                print("No token received in login response")
                raise StopUser()
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            raise StopUser()
    
    def get_auth_headers(self):
        """Get headers with authentication token"""
        if not self.token:
            return {"Content-Type": "application/json"}
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    @task(3)
    def get_user_dashboard(self):
        """Get user dashboard data"""
        self.client.get(
            "/identity/api/v2/user/dashboard",
            headers=self.get_auth_headers(),
            name="User: Dashboard"
        )
    
    @task(2)
    def get_vehicles(self):
        """Get user's vehicles"""
        self.client.get(
            "/identity/api/v2/vehicle/vehicles",
            headers=self.get_auth_headers(),
            name="Vehicle: Get Vehicles"
        )
    
    @task(1)
    def add_vehicle(self):
        """Add a new vehicle"""
        vehicle_data = {
            "vin": f"1HGBH41JXMN{random.randint(100000, 999999)}",
            "pincode": f"{random.randint(1000, 9999)}"
        }
        
        response = self.client.post(
            "/identity/api/v2/vehicle/add_vehicle",
            json=vehicle_data,
            headers=self.get_auth_headers(),
            name="Vehicle: Add Vehicle"
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if "id" in response_data:
                self.vehicle_id = response_data["id"]
    
    @task(2)
    def get_community_posts(self):
        """Get recent community posts"""
        self.client.get(
            "/community/api/v2/community/posts/recent",
            headers=self.get_auth_headers(),
            name="Community: Get Posts"
        )
    
    @task(1)
    def create_community_post(self):
        """Create a new community post"""
        post_data = {
            "title": f"Test Post {random.randint(1000, 9999)}",
            "content": f"This is a test post content created by load testing user at {random.randint(1000, 9999)}"
        }
        
        self.client.post(
            "/community/api/v2/community/posts",
            json=post_data,
            headers=self.get_auth_headers(),
            name="Community: Create Post"
        )
    
    @task(2)
    def get_shop_products(self):
        """Get shop products"""
        self.client.get(
            "/workshop/api/shop/products",
            headers=self.get_auth_headers(),
            name="Shop: Get Products"
        )
    
    @task(1)
    def get_mechanics(self):
        """Get available mechanics"""
        self.client.get(
            "/workshop/api/mechanic",
            headers=self.get_auth_headers(),
            name="Mechanic: Get Mechanics"
        )
    
    @task(1)
    def contact_mechanic(self):
        """Contact a mechanic for service"""
        if not self.vehicle_id:
            return  # Skip if no vehicle available
            
        service_data = {
            "mechanic_code": "MECH_001",
            "problem_details": f"Test service request {random.randint(1000, 9999)}",
            "vin": f"1HGBH41JXMN{random.randint(100000, 999999)}"
        }
        
        self.client.post(
            "/workshop/api/merchant/contact_mechanic",
            json=service_data,
            headers=self.get_auth_headers(),
            name="Mechanic: Contact Mechanic"
        )
    
    @task(1)
    def get_orders(self):
        """Get user's orders"""
        self.client.get(
            "/workshop/api/shop/orders/all",
            headers=self.get_auth_headers(),
            name="Shop: Get Orders"
        )


class CRAPIBrowsingUser(HttpUser):
    """
    Simulates users browsing the application without authentication
    """
    wait_time = between(2, 5)
    
    @task(5)
    def browse_homepage(self):
        """Browse the main homepage"""
        self.client.get("/", name="Browse: Homepage")
    
    @task(3)
    def browse_login_page(self):
        """Browse login page"""
        self.client.get("/login", name="Browse: Login Page")
    
    @task(2)
    def browse_signup_page(self):
        """Browse signup page"""
        self.client.get("/signup", name="Browse: Signup Page")
    
    @task(1)
    def browse_forum_page(self):
        """Browse forum page"""
        self.client.get("/forum", name="Browse: Forum Page")


class CRAPIAPIOnlyUser(HttpUser):
    """
    Simulates API-only usage (no web interface)
    Focus on high-frequency API calls
    """
    wait_time = between(0.5, 1.5)
    
    def on_start(self):
        """Setup API-only user with authentication"""
        self.signup_and_login()
    
    def signup_and_login(self):
        """Quick signup and login for API testing"""
        user_data = {
            "name": f"APIUser{random.randint(10000, 99999)}",
            "email": f"api{random.randint(10000, 99999)}@example.com",
            "number": f"555{random.randint(1000000, 9999999)}",
            "password": f"APIPass{random.randint(1000, 9999)}!"
        }
        
        signup_response = self.client.post(
            "/identity/api/auth/signup",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if signup_response.status_code != 200:
            raise StopUser()
        
        login_response = self.client.post(
            "/identity/api/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
        else:
            raise StopUser()
    
    def get_auth_headers(self):
        """Get headers with authentication token"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    @task(10)
    def rapid_dashboard_access(self):
        """High frequency dashboard access"""
        self.client.get(
            "/identity/api/v2/user/dashboard",
            headers=self.get_auth_headers(),
            name="API: Rapid Dashboard"
        )
    
    @task(5)
    def rapid_vehicle_check(self):
        """High frequency vehicle status check"""
        self.client.get(
            "/identity/api/v2/vehicle/vehicles",
            headers=self.get_auth_headers(),
            name="API: Rapid Vehicle Check"
        )
    
    @task(3)
    def rapid_posts_check(self):
        """High frequency posts check"""
        self.client.get(
            "/community/api/v2/community/posts/recent",
            headers=self.get_auth_headers(),
            name="API: Rapid Posts Check"
        )
