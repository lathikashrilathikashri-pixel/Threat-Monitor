"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: External Device Security Agent - Secure HTTPS Client
FILE: security-agent/api_client.py
===================================================================================
WHAT THIS FILE DOES:
    Provides robust, secure HTTPS communication between the agent and cloud backend:
    - Transmits heartbeat health pings to POST /api/devices/heartbeat
    - Ingests detected telemetry via POST /api/events
    - Self-registers new devices via POST /api/devices
    - Includes automatic exponential backoff retries, request timeouts, and 
      X-Device-Token authentication headers.

WHY IT IS REQUIRED:
    External devices must communicate reliably across unpredictable internet 
    connections. Proper timeout, error logging, and retry logic ensure telemetry 
    is never lost during transient network drops.

HOW IT CONNECTS TO OTHER MODULES:
    - Reads SERVER_URL and DEVICE_TOKEN from security-agent/config.py.
    - Used by security-agent/agent.py and simulate_events.py.
===================================================================================
"""

import time
import requests

class SOCApiClient:
    """Secure client for communicating with the deployed SOC REST API."""

    def __init__(self, server_url: str, device_token: str):
        self.server_url = server_url.rstrip("/")
        self.device_token = device_token
        self.headers = {
            "Content-Type": "application/json",
            "X-Device-Token": device_token,
            "User-Agent": "CyberSecurityAgent/1.0"
        }

    def send_heartbeat(self, device_id: str, os_type: str, ip_address: str) -> bool:
        """Sends periodic health status to maintain ONLINE status on the SOC dashboard."""
        url = f"{self.server_url}/api/devices/heartbeat"
        payload = {
            "device_id": device_id,
            "api_key": self.device_token,
            "os_type": os_type,
            "ip_address": ip_address
        }
        return self._post_with_retry(url, payload, description="Heartbeat Ping")

    def send_event(self, event_data: dict) -> dict | None:
        """Dispatches a security telemetry event for backend rule correlation."""
        url = f"{self.server_url}/api/events"
        return self._post_with_retry(url, event_data, description="Security Event Ingestion", return_json=True)

    def register_device(self, device_id: str, device_name: str, os_type: str, ip_address: str) -> dict | None:
        """Registers a fresh endpoint into the SOC asset database."""
        url = f"{self.server_url}/api/devices"
        payload = {
            "id": device_id,
            "device_name": device_name,
            "os_type": os_type,
            "ip_address": ip_address
        }
        return self._post_with_retry(url, payload, description="Device Registration", return_json=True)

    def _post_with_retry(self, url: str, payload: dict, description: str, max_retries: int = 3, return_json: bool = False):
        """Executes an HTTP POST with exponential backoff retry logic."""
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=8)
                if response.status_code in [200, 201]:
                    return response.json() if return_json else True
                else:
                    print(f"[-] {description} returned HTTP {response.status_code}: {response.text}")
                    return response.json() if return_json else False
            except requests.exceptions.RequestException as e:
                wait_time = attempt * 2
                print(f"[!] Warning: {description} attempt {attempt}/{max_retries} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

        print(f"[x] Error: {description} permanently failed after {max_retries} retries.")
        return None if return_json else False
