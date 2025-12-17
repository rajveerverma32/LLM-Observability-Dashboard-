"""
Demo script showing how to use the LLM Observability Backend API

This script demonstrates:
1. User registration and login
2. Logging LLM calls
3. Retrieving metrics
4. Managing feedback
5. Admin settings management
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Color codes for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message):
    """Print an info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def demo_auth():
    """Demonstrate authentication flow"""
    print_section("1. AUTHENTICATION DEMO")
    
    # Register new user
    print_info("Registering new user...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"testuser_{datetime.now().timestamp()}@example.com",
            "password": "password123"
        }
    )
    
    if register_response.status_code == 201:
        data = register_response.json()
        print_success(f"User registered: {data['user']['email']}")
        token = data['access_token']
    else:
        print_error(f"Registration failed: {register_response.text}")
        return None
    
    # Login with demo credentials
    print_info("\nLogging in with demo credentials...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "viewer@example.com",
            "password": "viewer123"
        }
    )
    
    if login_response.status_code == 200:
        data = login_response.json()
        print_success(f"Login successful for {data['user']['email']}")
        print_success(f"Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print_error(f"Login failed: {login_response.text}")
        return None


def demo_llm_logging(token):
    """Demonstrate LLM call logging"""
    print_section("2. LLM CALL LOGGING DEMO")
    
    # Log multiple LLM calls
    calls = [
        {"model_id": 1, "prompt_tokens": 50, "completion_tokens": 150, "latency_ms": 245.5},
        {"model_id": 2, "prompt_tokens": 100, "completion_tokens": 200, "latency_ms": 312.3},
        {"model_id": 3, "prompt_tokens": 75, "completion_tokens": 175, "latency_ms": 198.7},
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for i, call in enumerate(calls, 1):
        print_info(f"Logging LLM call {i}/3...")
        
        response = requests.post(
            f"{BASE_URL}/llm/log-call",
            headers=headers,
            json={
                **call,
                "total_tokens": call["prompt_tokens"] + call["completion_tokens"],
                "status": "success",
                "prompt_preview": f"Test prompt {i}",
                "response_preview": f"Test response {i}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Call logged (ID: {data['id']}, Latency: {call['latency_ms']}ms)")
        else:
            print_error(f"Failed to log call: {response.text}")


def demo_metrics(token):
    """Demonstrate metrics retrieval"""
    print_section("3. METRICS & ANALYTICS DEMO")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get metrics summary
    print_info("Fetching metrics summary...")
    response = requests.get(
        f"{BASE_URL}/metrics/summary?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Metrics Summary:")
        print(f"  • Total Tokens: {data['total_tokens']:,}")
        print(f"  • Total Cost: ${data['total_cost']:.4f}")
        print(f"  • Average Latency: {data['average_latency']:.2f}ms")
        print(f"  • Error Rate: {data['error_rate']:.2f}%")
    else:
        print_error(f"Failed to fetch metrics: {response.text}")
    
    # Get token usage
    print_info("\nFetching token usage...")
    response = requests.get(
        f"{BASE_URL}/metrics/token-usage?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Token usage data points: {len(data['data'])}")
        if data['data']:
            latest = data['data'][-1]
            print(f"  • Latest: {latest['date']} - {latest['tokens']} tokens, ${latest['cost']}")
    
    # Get latency distribution
    print_info("\nFetching latency distribution...")
    response = requests.get(
        f"{BASE_URL}/metrics/latency?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Latency Distribution:")
        for point in data['data']:
            print(f"  • {point['range']}: {point['count']} calls")
    
    # Get error rate
    print_info("\nFetching error rate...")
    response = requests.get(
        f"{BASE_URL}/metrics/error-rate?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Error rate data points: {len(data['data'])}")


def demo_feedback(token):
    """Demonstrate feedback submission"""
    print_section("4. FEEDBACK MANAGEMENT DEMO")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Submit feedback
    print_info("Submitting feedback for LLM call...")
    response = requests.post(
        f"{BASE_URL}/feedback",
        headers=headers,
        json={
            "llm_call_id": 1,
            "rating": 4,
            "comment": "Great response, very helpful and accurate"
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Feedback submitted (ID: {data['id']}, Rating: {data['rating']}/5)")
    else:
        print_error(f"Failed to submit feedback: {response.text}")


def demo_admin_settings(admin_token=None):
    """Demonstrate admin settings management"""
    print_section("5. ADMIN SETTINGS DEMO")
    
    if not admin_token:
        # Try to login as admin
        print_info("Logging in as admin...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "admin@example.com",
                "password": "admin123"
            }
        )
        
        if login_response.status_code != 200:
            print_error("Failed to login as admin")
            return
        
        admin_token = login_response.json()['access_token']
        print_success("Admin login successful")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get current settings
    print_info("\nFetching current system settings...")
    response = requests.get(f"{BASE_URL}/settings", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Current Settings:")
        print(f"  • Claude Haiku 4.5 Enabled: {data['claude_haiku_45_enabled']}")
        print(f"  • Max Tokens Per Request: {data['max_tokens_per_request']}")
        print(f"  • Caching Enabled: {data['enable_caching']}")
    else:
        print_error(f"Failed to fetch settings: {response.text}")
    
    # Update settings
    print_info("\nUpdating system settings (enabling Claude Haiku 4.5)...")
    response = requests.put(
        f"{BASE_URL}/settings",
        headers=headers,
        json={
            "claude_haiku_45_enabled": True,
            "max_tokens_per_request": 8192,
            "enable_caching": True
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Settings updated successfully")
        print(f"  • Claude Haiku 4.5 Enabled: {data['claude_haiku_45_enabled']}")
        print(f"  • Max Tokens Per Request: {data['max_tokens_per_request']}")
    else:
        print_error(f"Failed to update settings: {response.text}")


def main():
    """Run the demo"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  LLM OBSERVABILITY DASHBOARD - BACKEND API DEMO           ║")
    print("║  Demonstrating all major features and endpoints           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Check if server is running
    print_info("Checking if API server is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print_success("API server is running!")
        else:
            print_error("API server returned unexpected response")
            return
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API server at {BASE_URL}")
        print_error("Make sure the backend is running with: python main.py")
        return
    
    # Run demos
    token = demo_auth()
    if token:
        demo_llm_logging(token)
        demo_metrics(token)
        demo_feedback(token)
    
    demo_admin_settings()
    
    print_section("✓ DEMO COMPLETE")
    print("View the interactive API documentation at: http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
