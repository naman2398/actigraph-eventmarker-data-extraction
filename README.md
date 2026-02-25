# ActiGraph CentrePoint 3 Event Marker Extraction Tool

A lightweight, web-based tool for extracting Event Marker data from the ActiGraph CentrePoint 3 API.

**Live URL:** https://event-marker-data-export-cnczf6dkc3bne9gh.eastus2-01.azurewebsites.net  
**Tech Stack:** Python 3.12, Streamlit, Azure App Service  
**Package Manager:** uv (local) / pip (deployment)

## Project Structure

```
actigraph-eventmarker-data-extraction/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline for Azure deployment
├── docs/
│   └── design-doc.md           # Full design specification
├── src/
│   ├── __init__.py
│   ├── app.py                  # Main Streamlit application
│   └── api/
│       ├── __init__.py         # API module exports
│       ├── auth.py             # OAuth 2.0 token management
│       ├── subjects.py         # Subject list fetching
│       └── event_markers.py    # Event marker retrieval with pagination
├── .env.example                # Template for environment variables
├── startup.sh                  # Azure startup script
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project configuration
└── README.md
```

## Features

- ✅ OAuth 2.0 authentication with ActiGraph API
- ✅ Simple password-protected access
- ✅ Automatic subject list loading on login
- ✅ Subject selection via user-friendly identifiers
- ✅ Date range selection
- ✅ Automatic pagination for large datasets
- ✅ CSV export with download button
- ✅ Automated deployment via GitHub Actions

## Local Development

### Setup

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/naman2398/actigraph-eventmarker-data-extraction.git
   cd actigraph-eventmarker-data-extraction
   uv sync
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your credentials:
   ```
   CLIENT_ID=your_actigraph_client_id
   CLIENT_SECRET=your_actigraph_client_secret
   STUDY_ID=your_study_id
   APP_PASSWORD=your_app_password
   ```

### Run Locally

```bash
uv run streamlit run src/app.py
```

Open browser at `http://localhost:8501`

## Deployment

The application is deployed to Azure App Service with automatic CI/CD via GitHub Actions.

### Deployment Flow

1. Push to `main` branch triggers GitHub Actions workflow
2. Workflow installs dependencies and creates virtual environment
3. Application is deployed to Azure App Service
4. Startup script activates virtual environment and runs Streamlit

### Azure Configuration

**Required App Settings:**
| Name | Description |
|------|-------------|
| `CLIENT_ID` | ActiGraph API client ID |
| `CLIENT_SECRET` | ActiGraph API client secret |
| `STUDY_ID` | CentrePoint Study ID |
| `APP_PASSWORD` | Application login password |

**Startup Command:** `bash startup.sh`

### Manual Deployment

To trigger a manual deployment, go to GitHub Actions and run the workflow manually.

## Usage

1. Navigate to the application URL
2. Enter the application password
3. Wait for subjects to load automatically
4. Select a subject identifier from the dropdown
5. Choose start and end dates
6. Click "Fetch Event Markers"
7. View data preview and download as CSV

## API Documentation

- [Event Markers API](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/event_markers.md)
- [Authorization](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/authorization.md)
- [Scopes](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/scopes.md)
- [Scopes](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/scopes.md)

## Requirements

- Python 3.12+
- uv package manager
- ActiGraph CentrePoint 3 API credentials
Application to extract event marker data from actigraph software using API
