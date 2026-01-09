import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


def get_access_token() -> Optional[str]:
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.error("CLIENT_ID or CLIENT_SECRET not set in environment variables")
        return None
    
    token_url = "https://auth.actigraphcorp.com/connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    scopes_to_try = ["Analytics", "CentrePoint Analytics"]
    
    for scope in scopes_to_try:
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": scope
        }
        
        try:
            logger.info(f"Attempting authentication with scope: {scope}")
            response = requests.post(token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in")
                logger.info(f"Successfully obtained access token (expires in {expires_in}s)")
                return access_token
            else:
                logger.warning(f"Authentication failed with scope '{scope}': {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during authentication: {e}")
    
    logger.error("Failed to authenticate with all available scopes")
    return None
