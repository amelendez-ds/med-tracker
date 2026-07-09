import sys
import urllib.request
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class TriggerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    web_service_url: str
    cron_secret: str = ""


@lru_cache
def get_trigger_settings() -> TriggerSettings:
    return TriggerSettings()  # type: ignore[call-arg]


settings = get_trigger_settings()

if not settings.web_service_url or not settings.cron_secret:
    print("Missing Environment Variables! Check Render settings.")
    sys.exit(1)

# Build the secure request
target_endpoint = f"{settings.web_service_url}/daily-automation/"
request = urllib.request.Request(
    target_endpoint,
    headers={"authorization": f"Bearer {settings.cron_secret}"},
    method="POST",
)

# Send request
try:
    with urllib.request.urlopen(request) as response:
        print(f"Success! API Status: {response.status}")
        print(response.read().decode())
except Exception as e:
    print(f"Failed to trigger API: {e}")
