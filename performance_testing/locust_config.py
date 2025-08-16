"""
Locust Configuration for crAPI Performance Testing
Different test scenarios and configurations
"""

TEST_SCENARIOS = {
    "light_load": {
        "users": 10,
        "spawn_rate": 2,
        "run_time": "5m",
        "description": "Light load testing with 10 concurrent users"
    },
    "medium_load": {
        "users": 50,
        "spawn_rate": 5,
        "run_time": "10m",
        "description": "Medium load testing with 50 concurrent users"
    },
    "heavy_load": {
        "users": 100,
        "spawn_rate": 10,
        "run_time": "15m",
        "description": "Heavy load testing with 100 concurrent users"
    },
    "stress_test": {
        "users": 200,
        "spawn_rate": 20,
        "run_time": "20m",
        "description": "Stress testing with 200 concurrent users"
    }
}

PERFORMANCE_THRESHOLDS = {
    "response_time_95th_percentile": 2000,  # milliseconds
    "response_time_average": 500,  # milliseconds
    "error_rate": 0.05,  # 5% maximum error rate
    "requests_per_second": 100  # minimum RPS target
}

ENDPOINT_CATEGORIES = {
    "authentication": [
        "/identity/api/auth/signup",
        "/identity/api/auth/login",
        "/identity/api/auth/verify"
    ],
    "user_management": [
        "/identity/api/v2/user/dashboard",
        "/identity/api/v2/user/change-email",
        "/identity/api/v2/user/change-phone-number"
    ],
    "vehicle_operations": [
        "/identity/api/v2/vehicle/vehicles",
        "/identity/api/v2/vehicle/add_vehicle",
        "/identity/api/v2/vehicle/<carId>/location"
    ],
    "community_features": [
        "/community/api/v2/community/posts/recent",
        "/community/api/v2/community/posts",
        "/community/api/v2/community/posts/<postId>/comment"
    ],
    "workshop_services": [
        "/workshop/api/shop/products",
        "/workshop/api/shop/orders",
        "/workshop/api/mechanic",
        "/workshop/api/merchant/contact_mechanic"
    ]
}

USER_PATTERNS = {
    "normal_user": {
        "weight": 70,
        "description": "Regular users performing typical operations"
    },
    "browsing_user": {
        "weight": 20,
        "description": "Users browsing without authentication"
    },
    "api_heavy_user": {
        "weight": 10,
        "description": "API-heavy users with rapid requests"
    }
}
