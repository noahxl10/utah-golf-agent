import requests
import json
import time
import random
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import os


DEFAULT_EMAIL = os.environ["STONEBRIDGE_USERNAME"]
DEFAULT_PASSWORD = os.environ["STONEBRIDGE_PASSWORD"]
DEFAULT_COURSE_ID = os.environ["STONEBRIDGE_COURSE_ID"]
DEFAULT_BOOKING_CLASS_ID = "13900"
TOKEN_CACHE_FILE = "stonebridge_token_cache.json"

def login_stonebridge(
    email: str = DEFAULT_EMAIL,
    password: str = DEFAULT_PASSWORD,
    course_id: str = DEFAULT_COURSE_ID,
    booking_class_id: str = DEFAULT_BOOKING_CLASS_ID,
    api_key: str = "no_limits"
) -> Optional[Dict]:
    """
    Login to Stonebridge Golf Club API and get authentication token
    
    Args:
        email: User email
        password: User password
        course_id: Course ID
        booking_class_id: Booking class ID
        api_key: API key
        
    Returns:
        Dict with login response or None if login failed
    """
    url = os.environ["STONEBRIDGE_ENDPOINT"]
    
    # Build payload
    payload = {
        'username': email,
        'password': password,
        'booking_class_id': booking_class_id,
        'api_key': api_key,
        'course_id': course_id
    }
    
    headers = {
        # Authority and scheme headers
        ':authority': 'foreupsoftware.com',
        ':method': 'POST',
        ':path': '/index.php/api/booking/users/login',
        ':scheme': 'https',
        
        # Standard headers
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        
        # Security and request context
        'Origin': 'https://foreupsoftware.com',
        'Referer': f'https://foreupsoftware.com/index.php/booking/{course_id}',
        'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        
        # ForeUp specific headers
        'X-Requested-With': 'XMLHttpRequest',
        'X-Fu-Golfer-Location': 'foreup',
        'Api-Key': 'no_limits',
        'Priority': 'u=1, i'
    }

    # Add existing cookies if available
    if cookie:
        headers['Cookie'] = cookie

    try:
        print(f"Logging in as {email}...")

        # Convert payload to URL-encoded format
        form_data = "&".join(f"{key}={requests.utils.quote(str(value))}" for key, value in payload.items())

        response = requests.post(url, data=form_data, headers=headers, timeout=10)

        # Check for error status
        response.raise_for_status()

        # Parse response
        data = response.json()

        # Check if login was successful (jwt field should exist)
        if 'jwt' in data:
            print(f"✅ Login successful! Welcome {data.get('first_name', '')} {data.get('last_name', '')}")
            return data
        else:
            print("❌ Login failed: No JWT token in response")
            print(f"Response: {json.dumps(data, indent=2)}")
            return None

    except requests.Timeout:
        print("❌ Login failed: Request timed out")
        return None
    except requests.RequestException as e:
        print(f"❌ Login failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Login failed: Invalid JSON response - {e}")
        return None
    except Exception as e:
        print(f"❌ Login failed: Unexpected error - {e}")
        return None

def get_bearer_token(
    force_refresh: bool = False,
    email: str = DEFAULT_EMAIL,
    password: str = DEFAULT_PASSWORD
) -> Optional[Tuple[str, str]]:
    """
    Get a valid bearer token, using cache if available or logging in if needed
    
    Args:
        force_refresh: Force a new login even if cached token exists
        email: User email
        password: User password
        
    Returns:
        Tuple containing (bearer_token, cookie) or None if retrieval failed
    """
    # Try to load from cache first
    if not force_refresh:
        token_data = load_cached_token()
        if token_data and not is_token_expired(token_data.get('jwt')):
            print("Using cached token (still valid)")
            return token_data.get('jwt'), token_data.get('cookie')
    
    # Login to get new token
    login_data = login_stonebridge(email=email, password=password)
    
    if not login_data or 'jwt' not in login_data:
        print("Failed to get valid bearer token")
        return None
    
    # Get JWT token
    jwt_token = login_data.get('jwt')
    
    # Create realistic cookie string that matches browser cookies
    cookie = create_cookie_string()
    
    # Cache the token for future use
    cache_token(jwt_token, cookie)
    
    return jwt_token, cookie


def generate_session_id() -> str:
    """Generate a random session ID for the PHPSESSID cookie"""
    import random
    import string
    # Generate random 26-character string (similar to PHP session IDs)
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=26))


def create_cookie_string(phpsessid: str = None) -> str:
    """Create a cookie string similar to the browser's cookies"""
    if not phpsessid:
        phpsessid = generate_session_id()
        
    # Base cookie with required values
    cookie_parts = [
        f"PHPSESSID={phpsessid}",
        f"_gid=GA1.2.{random.randint(10000000, 99999999)}.{int(time.time())}",
        f"__stripe_mid={generate_uuid_like()}",
        f"__stripe_sid={generate_uuid_like()}",
        "_gat_gtag_UA_101056671_2=1",
        f"_ga_Y0N3BHPPWG=GS1.1.{int(time.time())}.1.1.{int(time.time())}.0.0.0",
        f"_ga=GA1.1.{random.randint(100000000, 999999999)}.{int(time.time())}"
    ]
    
    return "; ".join(cookie_parts)

def generate_uuid_like() -> str:
    """Generate a string similar to a UUID with some extra characters"""
    import uuid
    base_uuid = str(uuid.uuid4())
    extra_chars = ''.join(random.choices(string.hexdigits.lower(), k=6))
    return f"{base_uuid}{extra_chars}"

def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired"""
    try:
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return True
        
        # Decode the middle part (payload)
        import base64
        # Ensure proper padding
        payload = parts[1]
        payload += '=' * ((4 - len(payload) % 4) % 4)
        decoded_payload = base64.b64decode(payload)
        token_data = json.loads(decoded_payload)
        
        # Check expiration time
        exp_time = token_data.get('exp', 0)
        current_time = int(time.time())
        
        # Add 5-minute buffer to avoid using tokens that are about to expire
        return current_time + 300 >= exp_time
        
    except Exception as e:
        print(f"Error checking token expiration: {e}")
        # If there's any error parsing the token, consider it expired
        return True


def cache_token(jwt_token: str, cookie: str) -> None:
    """Save token to cache file"""
    cache_data = {
        'jwt': jwt_token,
        'cookie': cookie,
        'cached_at': int(time.time())
    }

    try:
        with open(TOKEN_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
        print(f"Token cached successfully to {TOKEN_CACHE_FILE}")
    except Exception as e:
        print(f"Failed to cache token: {e}")


def load_cached_token() -> Optional[Dict]:
    """Load token from cache file if it exists"""
    try:
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load cached token: {e}")

    return None


def get_token_expiration_time(token: str) -> Optional[datetime]:
    """Get the expiration time of a JWT token as a datetime object"""
    try:
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Decode the middle part (payload)
        import base64
        # Ensure proper padding
        payload = parts[1]
        payload += '=' * ((4 - len(payload) % 4) % 4)
        decoded_payload = base64.b64decode(payload)
        token_data = json.loads(decoded_payload)

        # Get expiration timestamp
        exp_time = token_data.get('exp', 0)
        if exp_time:
            return datetime.fromtimestamp(exp_time)
        return None

    except Exception as e:
        print(f"Error getting token expiration: {e}")
        return None


def get_auth_headers(force_refresh: bool = False) -> Dict[str, str]:
    """
    Get authentication headers (Authorization and Cookie)
    
    Args:
        force_refresh: Force a new login even if cached token exists
        
    Returns:
        Dict with authentication headers
    """
    token_info = get_bearer_token(force_refresh=force_refresh)
    
    if not token_info:
        return {}
    
    bearer_token, cookie = token_info
    
    return {
        # Standard headers
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        
        # Authorization
        'X-Authorization': f'Bearer {bearer_token}',
        'Cookie': cookie,
        
        # Context headers
        'Referer': f'https://foreupsoftware.com/index.php/booking/{DEFAULT_COURSE_ID}',
        'Origin': 'https://foreupsoftware.com',
        'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        
        # ForeUp specific headers
        'X-Requested-With': 'XMLHttpRequest',
        'X-Fu-Golfer-Location': 'foreup',
        'Api-Key': 'no_limits',
        'Priority': 'u=1, i'
    }

# Main entry point for testing
if __name__ == "__main__":
    print("=" * 60)
    print("STONEBRIDGE AUTHENTICATION SYSTEM")
    print("=" * 60)
    
    # Get authentication headers
    auth_headers = get_auth_headers()
    
    if auth_headers:
        print("\nAuthentication successful!")
        
        # Get token expiration time
        token = auth_headers.get('X-Authorization', '').replace('Bearer ', '')
        exp_time = get_token_expiration_time(token)
        
        if exp_time:
            print(f"Token valid until: {exp_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Calculate time remaining
            now = datetime.now()
            time_remaining = exp_time - now
            days = time_remaining.days
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            print(f"Time remaining: {days} days, {hours} hours, {minutes} minutes")
        
        print("\nAuthentication Headers:")
        print("-" * 60)
        for key, value in auth_headers.items():
            # Truncate long values for display
            display_value = value
            if len(value) > 50 and key != 'Cookie':
                display_value = value[:47] + "..."
            print(f"{key}: {display_value}")
        
        print("\nTest authentication by using these headers in stonebridge.py")
        print("Example usage:")
        print("-" * 60)
        print("from stonebridge_auth import get_bearer_token")
        print("bearer_token, cookie = get_bearer_token()")
        print("data = get_stonebridge_teetimes(")
        print("    date_str='08-28-2025',")
        print("    bearer_token=bearer_token,")
        print("    cookie=cookie")
        print(")")
    else:
        print("\nFailed to authenticate. Please check credentials.")

    print("\n" + "=" * 60)
