import os
import logging
from datetime import date
import streamlit as st
import pandas as pd

from api import get_access_token, clear_token_cache, fetch_subjects, fetch_event_markers

# Load environment variables from .env file (local development only)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not needed in production (Azure injects env vars)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="CentrePoint Event Marker Data Export",
    page_icon=None,
    layout="centered"
)

# Constants
STUDY_ID = os.getenv("STUDY_ID", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")


def check_password() -> bool:
    """Check if the user has entered the correct application password."""
    
    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # If already authenticated, return True
    if st.session_state.authenticated:
        return True
    
    # Show login form (header rendered by caller)
    st.markdown("---")
    
    # Password input
    password = st.text_input(
        "Enter application password to continue",
        type="password",
        placeholder="Password",
        key="password_input"
    )
    
    # Login button
    if st.button("Login", type="primary"):
        if not APP_PASSWORD:
            st.error("Application password not configured. Please contact administrator.")
            logger.error("APP_PASSWORD environment variable not set")
            return False
        
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            logger.info("User authenticated successfully")
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
            logger.warning("Failed login attempt")
    
    return False


def initialize_session() -> bool:
    """Initialize session and fetch subjects on first load."""
    
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    
    if st.session_state.initialized:
        return True
    
    # Show initialization message (header rendered by caller)
    with st.spinner("Loading..."):
        try:
            # Get access token (combined CentrePoint+Analytics scope)
            token = get_access_token()
            if not token:
                st.error("Failed to authenticate with API. Please check your credentials.")
                return False
            
            # Fetch subjects
            subjects = fetch_subjects(token, STUDY_ID)
            if subjects:
                st.session_state.subject_mapping = subjects
                st.session_state.initialized = True
                logger.info(f"Loaded {len(subjects)} subjects")
                st.success("Subject list loaded successfully!")
                st.rerun()
            else:
                st.error("Failed to fetch subject list. Please check your Study ID.")
                return False
        except Exception as e:
            st.error(f"Error during initialization: {str(e)}")
            logger.error(f"Initialization error: {str(e)}")
            return False
    
    return False


def refresh_subjects():
    """Refresh subject list from API."""
    with st.spinner("Refreshing subject list..."):
        try:
            token = get_access_token()
            if token:
                subjects = fetch_subjects(token, STUDY_ID)
                if subjects:
                    st.session_state.subject_mapping = subjects
                    logger.info(f"Refreshed {len(subjects)} subjects")
                    st.success("Subject list refreshed!")
                else:
                    st.error("Failed to fetch subject list")
            else:
                st.error("Failed to get access token")
        except Exception as e:
            st.error(f"Error refreshing subjects: {str(e)}")
            logger.error(f"Error refreshing subjects: {str(e)}")


def main():
    """Main application logic."""
    
    # Initialize session and fetch subjects
    if not initialize_session():
        return
    
    # Main dashboard (header rendered at top level)
    st.markdown("---")
    
    # Add refresh button in sidebar
    with st.sidebar:
        st.markdown("##### Controls")
        if st.button("Refresh Subject List"):
            refresh_subjects()
            st.rerun()
    
    # Check if we have subject mapping
    if "subject_mapping" not in st.session_state or not st.session_state.subject_mapping:
        st.error("No subjects available. Please refresh the page.")
        return
    
    subject_mapping = st.session_state.subject_mapping
    subject_identifiers = sorted(subject_mapping.keys())
    
    # Sidebar for logout
    with st.sidebar:
        st.markdown("### Session Info")
        st.info(f"**Subjects Loaded:** {len(subject_identifiers)}")
        if st.button("Logout"):
            clear_token_cache()
            st.session_state.clear()
            st.rerun()
    
    # Subject selection
    st.markdown("##### Subjects")
    selected_identifier = st.selectbox(
        "Subject Identifier:",
        options=["Select Subject"] + subject_identifiers,
        index=0,
        help="Select the subject identifier for data extraction"
    )
    
    # Date range selection
    st.markdown("##### Date Range")
    col1, col2 = st.columns(2)
    
    with col1:
        from_date = st.date_input(
            "From Date:",
            value=None,
            max_value=date.today(),
            format="YYYY-MM-DD",
            help="Start date for data extraction (YYYY-MM-DD)"
        )
    
    with col2:
        to_date = st.date_input(
            "To Date:",
            value=None,
            max_value=date.today(),
            format="YYYY-MM-DD",
            help="End date for data extraction (YYYY-MM-DD)"
        )
    
    # Fetch data button
    if st.button("Fetch Event Markers", type="primary"):
        # Validate subject selection
        if selected_identifier == "Select Subject":
            st.error("Please select a subject")
            return
        
        # Validate date selection
        if from_date is None or to_date is None:
            st.error("Please select both From Date and To Date")
            return
        
        if from_date > to_date:
            st.error("From Date must be before To Date")
            return
        
        # Get Subject ID from mapping
        subject_id = subject_mapping[selected_identifier]
        
        with st.spinner("Fetching event markers..."):
            # Get access token (auto-refreshes if expired)
            token = get_access_token()
            if not token:
                st.error("Authentication failed. Please logout and login again.")
                return
            
            # Fetch event markers
            result = fetch_event_markers(
                access_token=token,
                study_id=STUDY_ID,
                subject_id=subject_id,
                from_date=from_date.isoformat(),
                to_date=to_date.isoformat()
            )
            
            if result is None:
                st.error("Failed to fetch event markers. Please try again.")
                return
            
            items = result.get("items", [])
            total_count = result.get("totalCount", 0)
            
            if total_count == 0:
                st.warning("No event markers found for the selected date range.")
                return
            
            # Display results
            st.success(f"Retrieved {total_count} event markers")
            
            # Convert to DataFrame and add subject_identifier column
            df = pd.DataFrame(items)
            df.insert(0, "subject_identifier", selected_identifier)

            # Add Eastern Time column derived from timestampUtc
            if "timestampUtc" in df.columns:
                et_col = (
                    pd.to_datetime(df["timestampUtc"], utc=True)
                    .dt.tz_convert("America/New_York")
                    .dt.strftime("%Y-%m-%dT%H:%M:%S%z")
                )
                et_position = df.columns.get_loc("timestampUtc") + 1
                df.insert(et_position, "timestampET", et_col)

            # Display all records (scrollable)
            st.markdown("##### Data Preview")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download button
            csv = df.to_csv(index=False)
            filename = f"event_markers_{selected_identifier}_{from_date}_{to_date}.csv"
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )
            
            st.info(f"**Total Records:** {len(df)}")


if __name__ == "__main__":
    # Render header once at top level
    st.markdown("#### CentrePoint Event Marker Data Export")
    
    if not STUDY_ID:
        st.error("STUDY_ID environment variable is not set. Please contact administrator.")
        logger.error("STUDY_ID not configured")
    elif not check_password():
        # Stop here if not authenticated
        pass
    else:
        main()
