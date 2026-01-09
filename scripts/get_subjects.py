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


def list_subjects(access_token: str, study_id: str) -> None:
    """Retrieve and display all subjects for a study."""
    url = f"https://api.actigraphcorp.com/centrepoint/v3/Studies/{study_id}/Subjects"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    try:
        logger.info(f"Fetching subjects for Study ID: {study_id}...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            subjects = data.get("items", [])
            
            if not subjects:
                logger.warning("No subjects found")
                return
            
            logger.info(f"Found {len(subjects)} subject(s):\n")
            for subject in subjects:
                print(f"Subject ID (numeric): {subject.get('id')}")
                print(f"Subject Identifier: {subject.get('subjectIdentifier')}")
                print(f"Site Identifier: {subject.get('siteIdentifier')}")
                print(f"Gender: {subject.get('gender')}")
                print(f"Wear Position: {subject.get('wearPosition')}")
                print(f"Assignment Status: {subject.get('assignmentStatus')}")
                print("-" * 50)
        else:
            logger.error(f"Failed to fetch subjects: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")


def main():
    load_dotenv()
    
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    study_id = os.getenv("STUDY_ID")
    
    if not client_id or not client_secret:
        logger.error("CLIENT_ID and CLIENT_SECRET must be set in .env file")
        return
    
    if not study_id:
        logger.error("STUDY_ID must be set in .env file")
        return
    
    access_token = get_access_token(client_id, client_secret)
    if not access_token:
        return
    
    list_subjects(access_token, study_id)


if __name__ == "__main__":
    main()
