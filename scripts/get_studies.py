import os
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_access_token(client_id: str, client_secret: str) -> str | None:
    """Authenticate and retrieve access token."""
    url = "https://auth.actigraphcorp.com/connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "CentrePoint"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            logger.info("Successfully obtained access token")
            return token
        else:
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Authentication request error: {e}")
        return None


def list_studies(access_token: str) -> None:
    """Retrieve and display all available studies."""
    url = "https://api.actigraphcorp.com/centrepoint/v3/Studies"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    try:
        logger.info("Fetching studies...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            studies = data.get("items", [])
            
            if not studies:
                logger.warning("No studies found")
                return
            
            logger.info(f"Found {len(studies)} study/studies:\n")
            for study in studies:
                print(f"Study ID: {study.get('id')}")
                print(f"Name: {study.get('name')}")
                print(f"Site ID: {study.get('siteId')}")
                print(f"Site Name: {study.get('siteName')}")
                print("-" * 50)
        else:
            logger.error(f"Failed to fetch studies: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")


def main():
    load_dotenv()
    
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.error("CLIENT_ID and CLIENT_SECRET must be set in .env file")
        return
    
    access_token = get_access_token(client_id, client_secret)
    if not access_token:
        return
    
    list_studies(access_token)


if __name__ == "__main__":
    main()
