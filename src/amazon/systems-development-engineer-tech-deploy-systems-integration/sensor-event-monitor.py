"""
You’re integrating a new sensor into a deployment system. The sensor emits an event each time a package passes. 
Write a Python script that listens to sensor data (simulated), logs each detection with a timestamp, and raises an alert if no package is detected for more than 5 seconds.

✅ Expected Skills:
Threading / async

Logging

Timer/reset logic
"""

import time
import threading
from datetime import datetime

# Simulate sensor input (in production, this would be a GPIO read or API callback)
def sensor_simulator(event_callback):
    while True:
        time.sleep(2)  # Simulates a package every 2 seconds
        event_callback()

# Logger
def log_detection():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Package detected.")

# Alert function
def alert_on_timeout():
    print("[ALERT] No package detected in the last 5 seconds!")

# Monitoring logic
class SensorMonitor:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.last_event_time = time.time()
        self.lock = threading.Lock()
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def sensor_event(self):
        with self.lock:
            self.last_event_time = time.time()
        log_detection()

    def monitor(self):
        while True:
            time.sleep(1)
            with self.lock:
                if time.time() - self.last_event_time > self.timeout:
                    alert_on_timeout()
                    self.last_event_time = time.time()  # reset to avoid repeated alerts

if __name__ == "__main__":
    monitor = SensorMonitor(timeout=5)
    sensor_simulator(monitor.sensor_event)
