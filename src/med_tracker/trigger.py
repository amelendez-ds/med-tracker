import os
import urllib.request

# Grab our secrets from Render
app_url = os.getenv("WEB_SERVICE_URL")
cron_secret = os.getenv("CRON_SECRET")

if not app_url or not cron_secret:
    print("Missing Environment Variables! Check Render settings.")
    exit(1)

# Build the secure request
target_endpoint = f"{app_url}/daily-automation/"
request = urllib.request.Request(
    target_endpoint, headers={"authorization": f"Bearer {cron_secret}"}, method="POST"
)

# Send request
try:
    with urllib.request.urlopen(request) as response:
        print(f"Success! API Status: {response.status}")
        print(response.read().decode())
except Exception as e:
    print(f"Failed to trigger API: {e}")
