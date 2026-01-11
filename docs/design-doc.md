# Design Document: CentrePoint 3 Event Marker Extraction Tool

**Date:** January 09, 2026  
**Status:** Final Draft (Revision 3)  
**Target Audience:** LLM / Developer  
**Python Version:** 3.12  
**Package Manager:** uv

## References

- [Event Markers API Documentation](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/event_markers.md)
- [Scopes Documentation](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/scopes.md)
- [Authorization Documentation](https://github.com/actigraph/CentrePoint3APIDocumentation/blob/main/sections/authorization.md)

---

## 1. Project Overview

**Objective:** Create a lightweight, web-based tool that allows non-technical users to extract "Event Marker" data from the ActiGraph CentrePoint 3 API. The tool will be hosted on Azure and accessible via a public URL, protected by a simple application-level password.

**Tech Stack:**
- **Language:** Python 3.12
- **Framework:** Streamlit (for UI and backend logic)
- **Package Manager:** uv (for ultra-fast dependency management and virtual environments)
- **Hosting:** Azure App Service (Linux Web App)
- **CI/CD:** GitHub Actions

---

## 2. API Integration Specifications

Derived from ActiGraph CentrePoint 3 Documentation.

### A. Authentication (OAuth 2.0 Client Credentials)

- **Endpoint:** `https://auth.actigraphcorp.com/connect/token`
- **Method:** POST
- **Headers:** `Content-Type: application/x-www-form-urlencoded`
- **Body Parameters:**
  - `client_id`: [Provided via Env Variable]
  - `client_secret`: [Provided via Env Variable]
  - `grant_type`: `client_credentials`
  - `scope`: `Analytics` (Note: If this fails, retry with `CentrePoint Analytics` as the scope string)
- **Expected Response:** JSON object containing `access_token` (Bearer token) and `expires_in`

### B. Data Retrieval (Event Markers)

- **Endpoint:** `https://api.actigraphcorp.com/analytics/v3/Studies/{studyId}/Subjects/{subjectId}/EventMarkers`
- **Method:** GET
- **Headers:**
  - `Authorization: Bearer {access_token}`
  - `Accept: application/json`
- **Query Parameters:**
  - `fromDate`: ISO8601 Date format (e.g., `2024-01-01`)
  - `toDate`: ISO8601 Date format (e.g., `2024-01-31`)
- **Pagination Handling:**
  - The API returns a `totalCount` field
  - The logic must implement offsets or follow "next page" links if the `totalCount` exceeds the default page size (typically 100 records)

---

## 3. Implementation Phases

This project will be executed in three distinct phases.

### Phase 1: API Connection Verification (Local Dev)

**Goal:** Validate ActiGraph Client Credentials and understand the API response structure without building the UI.

**Environment Setup:**
- Initialize a new Python project using `uv`
- Create a virtual environment with Python 3.12
- Install `requests` using `uv`

**Authentication Logic:**
- Implement the OAuth 2.0 flow using the Authentication details in Section 2A
- Print the generated Access Token to the console to verify success

**Data Retrieval Logic:**
- Hardcode a specific Study ID and Subject ID for testing
- Construct the GET request using the Data Retrieval details in Section 2B
- Print the raw JSON response to the console to verify the presence of event marker data (timestamp, payload, etc.)

**Outcome:** A standalone Python script that successfully prints a valid token and a JSON list of event markers.

---

### Phase 2: Application Development (Local Streamlit)

**Goal:** Build the interactive user interface and full data extraction logic.

**UI Layout:**
- **Initialization:** On first load, the application automatically:
  1. Authenticates with the ActiGraph API using CLIENT_ID and CLIENT_SECRET from environment variables
  2. Fetches the complete list of subjects from `/Studies/{studyId}/Subjects` endpoint
  3. Builds an internal mapping of Subject Identifier → Subject ID
  4. Displays success message when ready
- **Main Dashboard:**
  - Study ID is hardcoded in environment variables (not visible to user)
  - Dropdown menu for Subject Identifier selection (user-friendly names)
  - Date pickers for Start Date and End Date
  - A primary "Fetch Data" action button
  - Sidebar with "Refresh Subject List" button to manually update the subject list

**Backend Processing:**
- **Subject List Fetcher:** On successful login, retrieve all subjects from the `/Studies/{studyId}/Subjects` endpoint and create an internal dictionary mapping Subject Identifier (string) to Subject ID (numeric)
- **Subject ID Resolution:** When user selects a Subject Identifier from dropdown, internally resolve it to the corresponding Subject ID for the API call
- **Pagination Handler:** Implement a loop that checks the `totalCount` from the API response and automatically fetches subsequent pages until all records are retrieved
- **Data Formatting:** Flatten the JSON response into a Pandas DataFrame
- **Export Utility:** Convert the DataFrame to CSV and render a `st.download_button`

**Dependency Management:**
- Use `uv` to add `streamlit` and `pandas`
- Generate a `requirements.txt` file from the `uv` lockfile

**Outcome:** A fully functional application running on localhost where a user can log in (triggering subject list refresh), select subjects by their identifier, fetch data, and download a CSV.

---

### Phase 3: Deployment (Azure & GitHub Actions)

**Goal:** Make the application accessible via a public URL with automated updates.

**Infrastructure Preparation:**
- **Azure Web App:** Provision a Linux-based App Service running Python 3.12
- **Startup Configuration:** Configure the Azure startup command:  
  `python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0`

**CI/CD Pipeline (GitHub Actions):**
- Create a workflow file (`.github/workflows/deploy.yml`) that triggers on push to `main`
- **Build Step:**
  - Check out code
  - Set up Python 3.12
  - Install dependencies using `uv` (or pip via `requirements.txt` generated by `uv`)
- **Deploy Step:**
  - Authenticate with Azure using the Publish Profile
  - Deploy the artifact to the Azure Web App

**Security Configuration:**
- **Secrets Management:** Store `CLIENT_ID`, `CLIENT_SECRET`, and `APP_PASSWORD` as Environment Variables in the Azure App Service (Configuration → Application Settings)
- Ensure the Python code retrieves these values using `os.getenv()`

**Outcome:** The tool is live at `https://[app-name].azurewebsites.net` and updates automatically on `git push`.