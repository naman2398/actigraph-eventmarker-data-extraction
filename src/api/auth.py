import os
import logging
import time
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level token cache
_token_cache: dict = {
    "access_token": None,
    "expires_at": 0
}


def get_access_token() -> Optional[str]:
    """
    Get access token for ActiGraph API with automatic refresh.
    
    Uses combined CentrePoint+Analytics scope for both subjects and event markers APIs.
    Caches token and auto-refreshes when expired or about to expire (< 5 min remaining).
    """
    global _token_cache
    
    # Check if cached token is still valid (with 5 min buffer)
    if _token_cache["access_token"] and time.time() < (_token_cache["expires_at"] - 300):
        logger.debug("Using cached access token")
        return _token_cache["access_token"]
    
    # Need to fetch new token
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.error("CLIENT_ID or CLIENT_SECRET not set in environment variables")
        return None
    
    token_url = "https://auth.actigraphcorp.com/connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    # Use combined scope for both CentrePoint (subjects) and Analytics (event markers)
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "CentrePoint Analytics"
    }
    
    try:
        logger.info("Requesting new access token with scope: CentrePoint Analytics")
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            
            # Cache token with expiration timestamp
            _token_cache["access_token"] = access_token
            _token_cache["expires_at"] = time.time() + expires_in
            
            logger.info(f"Successfully obtained access token (expires in {expires_in}s)")
            return access_token
        else:
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during authentication: {e}")
        return None


def clear_token_cache():
    """Clear the cached token (useful for logout/refresh)."""
    global _token_cache
    _token_cache = {"access_token": None, "expires_at": 0}
    logger.info("Token cache cleared")
