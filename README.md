# ActiGraph CentrePoint 3 Event Marker Extraction Tool

A lightweight, web-based tool for extracting Event Marker data from the ActiGraph CentrePoint 3 API.

**Tech Stack:** Python 3.12, Streamlit, Azure App Service  
**Package Manager:** uv

## Project Structure

```
actigraph-eventmarker-data-extraction/
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD pipeline for Azure deployment (Phase 3)
├── src/
│   ├── __init__.py
│   ├── auth.py                     # OAuth 2.0 authentication module
│   ├── event_markers.py            # Event marker data retrieval
│   └── app.py                      # Streamlit application (Phase 2)
├── scripts/
│   └── verify_api.py               # Phase 1: API connection verification
├── .env.example                    # Template for environment variables
├── .gitignore
├── requirements.txt                # Python dependencies (generated from uv)
├── pyproject.toml                  # uv project configuration
├── centrepoint-design-doc.md       # Full design specification
└── README.md
```

## Development Phases

### Phase 1: API Connection Verification ✅

Validate ActiGraph credentials and API connectivity.

**Setup:**
1. Create environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   - `CLIENT_ID`: ActiGraph API client ID
   - `CLIENT_SECRET`: ActiGraph API client secret
   - `STUDY_ID`: Study ID for testing
   - `APP_PASSWORD`: Password for application access
   - `SUBJECT_ID`: Subject ID for testing (Phase 1 only)
   - `FROM_DATE` / `TO_DATE`: Date range (YYYY-MM-DD, Phase 1 only)

3. Run verification script:
   ```bash
   uv run python scripts/verify_api.py
   ```

### Phase 2: Application Development ✅

Build the interactive Streamlit interface with subject identifier dropdown.

**Features:**
- Simple password-based authentication
- Automatic subject list refresh on login
- Subject selection via user-friendly identifiers (not numeric IDs)
- Internal mapping of Subject Identifier → Subject ID
- Date range selection
- CSV export functionality

**Run Locally:**
```bash
uv run streamlit run src/app.py
```

**Usage:**
1. Open browser at `http://localhost:8501`
2. Enter the application password (from `.env`)
3. Wait for subjects to load (happens automatically after login)
4. Select subject identifier from dropdown
5. Choose date range
6. Click "Fetch Event Markers"
7. Download CSV
   uv run scripts/verify_api.py
   ```

### Phase 2: Streamlit Application (In Progress)

Build interactive UI for data extraction with CSV export.

**Coming soon:**
- Password-protected interface
- Interactive date/ID selectors
- Automatic pagination handling
- CSV download functionality

### Phase 3: Azure Deployment (Planned)

Deploy to Azure App Service with GitHub Actions CI/CD.

## API Documentation

- [Event Markers API](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/event_markers.md)
- [Authorization](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/authorization.md)
- [Scopes](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/scopes.md)

## Requirements

- Python 3.12+
- uv package manager
- ActiGraph CentrePoint 3 API credentials
Application to extract event marker data from actigraph software using API
