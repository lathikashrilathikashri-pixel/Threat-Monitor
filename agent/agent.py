"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: External Device Security Agent - Main Daemon
FILE: security-agent/agent.py
===================================================================================
WHAT THIS FILE DOES:
    Main continuous monitoring daemon designed to run on an external laptop, VM,
    or server. It runs background threads/loops:
    1. Sends periodic heartbeat pings to keep the endpoint ONLINE on the SOC dashboard.
    2. Collects network sockets and process snapshots.
    3. Runs anomaly detection to flag unauthorized security tools and abnormal connections.
    4. Transmits flagged events securely over HTTPS to the cloud backend.
    5. Writes local audit logs to agent_telemetry.log.

WHY IT IS REQUIRED:
    Fulfills the core architectural requirement of connecting an external physical or 
    virtual machine to the cloud monitoring system over the internet.

HOW IT CONNECTS TO OTHER MODULES:
    - Imports collector.py, detector.py, api_client.py, config.py.
    - Sends REST API calls to the Flask backend running locally or in the cloud.
===================================================================================
"""

import sys
import time
import logging
from datetime import datetime, timezone
import platform

from config import (
    SERVER_URL, DEVICE_ID, DEVICE_TOKEN, HEARTBEAT_INTERVAL, 
    TELEMETRY_INTERVAL, LOG_FILE
)
from collector import SystemTelemetryCollector
from detector import LocalSecurityDetector
from api_client import SOCApiClient

# Configure agent logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SOC-Agent")

def run_agent():
    """Starts the continuous endpoint security monitoring loop."""
    logger.info("=" * 65)
    logger.info("CYBERSECURITY ENDPOINT MONITORING AGENT INITIALIZING")
    logger.info(f"Target Server URL: {SERVER_URL}")
    logger.info(f"Device ID:         {DEVICE_ID}")
    logger.info(f"OS Architecture:   {platform.system()} {platform.release()} ({platform.machine()})")
    logger.info("=" * 65)

    client = SOCApiClient(server_url=SERVER_URL, device_token=DEVICE_TOKEN)
    collector = SystemTelemetryCollector(device_id=DEVICE_ID)
    detector = LocalSecurityDetector(device_id=DEVICE_ID)

    # Initial registration / connection handshake
    host_summary = collector.collect_system_summary()
    logger.info("[*] Performing initial endpoint handshake with cloud backend...")
    reg_result = client.register_device(
        device_id=DEVICE_ID,
        device_name=f"Endpoint {platform.node()}",
        os_type=f"{platform.system()} {platform.release()}",
        ip_address=host_summary["ip_address"]
    )
    if reg_result:
        logger.info("[OK] Handshake verified. Device registered in SOC asset database.")
    else:
        logger.warning("[!] Handshake warning (device may already be registered). Proceeding...")

    last_heartbeat_time = 0
    last_telemetry_time = 0

    logger.info("[*] Security monitoring loop active. Press Ctrl+C to terminate.")

    try:
        while True:
            current_time = time.time()

            # 1. Periodic Heartbeat
            if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                summary = collector.collect_system_summary()
                success = client.send_heartbeat(
                    device_id=DEVICE_ID,
                    os_type=summary["os_version"],
                    ip_address=summary["ip_address"]
                )
                if success:
                    logger.info(f"[+] Heartbeat sent successfully (CPU: {summary.get('cpu_percent', 0)}%, RAM: {summary.get('ram_percent', 0)}%)")
                else:
                    logger.warning("[-] Heartbeat ping failed. Will retry next cycle.")
                last_heartbeat_time = current_time

            # 2. Telemetry and Anomaly Detection
            if current_time - last_telemetry_time >= TELEMETRY_INTERVAL:
                summary = collector.collect_system_summary()
                host_ip = summary["ip_address"]

                # Scan running processes
                processes = collector.collect_running_processes()
                process_events = detector.evaluate_processes(processes, host_ip)
                for event in process_events:
                    logger.warning(f"[!] DETECTED SUSPICIOUS PROCESS: {event.get('process_name')} - Dispatching alert to SOC!")
                    client.send_event(event)

                # Scan active network sockets
                connections = collector.collect_network_connections()
                connection_events = detector.evaluate_connections(connections, host_ip)
                for event in connection_events:
                    logger.warning(f"[!] DETECTED ANOMALOUS CONNECTION: Port {event.get('destination_port')} - Dispatching alert to SOC!")
                    client.send_event(event)

                last_telemetry_time = current_time

            time.sleep(2)

    except KeyboardInterrupt:
        logger.info("[*] User interrupted agent daemon. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"[x] Fatal error in agent execution: {e}", exc_info=True)

if __name__ == "__main__":
    run_agent()
