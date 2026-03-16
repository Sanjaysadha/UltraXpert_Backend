import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
EXPORT_URL = f"{BASE_URL}/api/v1/export/report"

def test_connectivity():
    print("--- Connectivity Test Starting ---")
    
    # 1. Login to get token (using a common test account)
    # Note: Replace with your actual credentials if they differ
    test_creds = {"username": "doctor@example.com", "password": "password"}
    try:
        login_res = requests.post(LOGIN_URL, data=test_creds)
        if login_res.status_code != 200:
            print(f"FAILED: Login failed ({login_res.status_code}). Please use valid credentials.")
            return
        
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("SUCCESS: Logged in and received Auth Token.")

        # 2. Get a sample Report ID
        reports_res = requests.get(f"{BASE_URL}/api/v1/reports/", headers=headers)
        reports = reports_res.json()
        if not reports:
            print("FAILED: No reports found in DB to export.")
            return
        
        report_id = reports[0]["id"]
        print(f"SUCCESS: Found Report ID: {report_id}")

        # 3. Trigger Export
        export_data = {
            "report_id": report_id,
            "export_format": "PDF",
            "include_images": True,
            "include_notes": True
        }
        
        print(f"ACTION: Sending Export Request for {report_id}...")
        export_res = requests.post(EXPORT_URL, headers=headers, json=export_data)
        
        if export_res.status_code == 200:
            result = export_res.json()
            print("--- TEST CONCLUDED SUCCESSFULLY ---")
            print(f"MESSAGE: {result['message']}")
            print(f"FILE DOWNLOAD LINK: {result['file_url']}")
            print(f"NOTIFICATION CREATED: {result['notification']['title']}")
            print("\nPROMPT: Now open your app's Notification Screen. You will see 'Patient Detail' there.")
        else:
            print(f"FAILED: Export returned error {export_res.status_code}")
            print(export_res.text)

    except Exception as e:
        print(f"ERROR: Could not connect to server: {str(e)}")

if __name__ == "__main__":
    test_connectivity()
