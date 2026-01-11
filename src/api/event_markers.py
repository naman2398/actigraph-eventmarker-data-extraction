import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def fetch_event_markers(
    access_token: str,
    study_id: str,
    subject_id: str,
    from_date: str,
    to_date: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch all event markers for a subject with automatic pagination.
    
    Uses offset-based pagination to ensure all records are retrieved.
    """
    base_url = "https://api.actigraphcorp.com"
    endpoint = f"/analytics/v3/Studies/{study_id}/Subjects/{subject_id}/EventMarkers"
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    all_items: List[Dict[str, Any]] = []
    offset = 0
    limit = 100
    total_count = None
    
    try:
        logger.info(f"Fetching event markers for Study ID: {study_id}, Subject ID: {subject_id}")
        logger.info(f"Date range: {from_date} to {to_date}")
        
        while True:
            params = {
                "fromDate": from_date,
                "toDate": to_date,
                "offset": offset,
                "limit": limit
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch event markers: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            items = data.get("items", [])
            total_count = data.get("totalCount", 0)
            
            all_items.extend(items)
            
            logger.info(f"Retrieved {len(items)} items (offset: {offset}, total: {len(all_items)}/{total_count})")
            
            # Stop if we have all items or no more items returned
            if len(all_items) >= total_count or len(items) == 0:
                break
            
            # Move to next page
            offset += limit
        
        logger.info(f"Successfully retrieved all {len(all_items)} event markers")
        
        return {
            "items": all_items,
            "totalCount": len(all_items)
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching event markers: {e}")
        return None
