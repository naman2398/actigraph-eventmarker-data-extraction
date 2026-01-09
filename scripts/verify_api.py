import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auth import get_access_token
from event_markers import fetch_event_markers


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    load_dotenv()
    
    logger.info("Starting API connection verification")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to obtain access token. Exiting.")
        sys.exit(1)
    
    logger.info(f"Access token obtained: {access_token[:20]}...")
    
    study_id = os.getenv("STUDY_ID")
    subject_id = os.getenv("SUBJECT_ID")
    from_date = os.getenv("FROM_DATE", "2024-01-01")
    to_date = os.getenv("TO_DATE", "2024-01-31")
    
    if not study_id or not subject_id:
        logger.error("STUDY_ID and SUBJECT_ID must be set in environment variables")
        sys.exit(1)
    
    event_data = fetch_event_markers(
        access_token=access_token,
        study_id=study_id,
        subject_id=subject_id,
        from_date=from_date,
        to_date=to_date
    )
    
    if event_data:
        logger.info("Event marker data retrieved successfully")
        logger.info(json.dumps(event_data, indent=2))
    else:
        logger.error("Failed to retrieve event marker data")
        sys.exit(1)


if __name__ == "__main__":
    main()
