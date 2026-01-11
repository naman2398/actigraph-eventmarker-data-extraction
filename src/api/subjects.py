import logging
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def fetch_subjects(access_token: str, study_id: str) -> Optional[Dict[str, str]]:
    """
    Fetch all subjects for a study and return a mapping of Subject Identifier -> Subject ID.
    
    Args:
        access_token: Bearer token for API authentication
        study_id: The study ID to fetch subjects from
        
    Returns:
        Dictionary mapping Subject Identifier (string) to Subject ID (string), or None on error
    """
    url = f"https://api.actigraphcorp.com/centrepoint/v3/Studies/{study_id}/Subjects"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    try:
        logger.info(f"Fetching subjects for Study ID: {study_id}")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch subjects: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        subjects = data.get("items", [])
        
        # Create mapping: Subject Identifier -> Subject ID
        subject_mapping = {
            subject.get("subjectIdentifier"): str(subject.get("id"))
            for subject in subjects
            if subject.get("subjectIdentifier") and subject.get("id")
        }
        
        logger.info(f"Successfully fetched {len(subject_mapping)} subjects")
        return subject_mapping
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching subjects: {e}")
        return None
