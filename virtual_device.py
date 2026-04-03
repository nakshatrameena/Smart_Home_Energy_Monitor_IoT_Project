import time
import random
import requests
import json

# ThingsBoard Cloud URL & token
url = "https://thingsboard.cloud/api/v1/Twxv1yhVrF3fqhyzcQsy/telemetry"

voltage = 230.0
powerThreshold = 2000

while True:
    # Simulate sensor reading (0-1023 like analogRead)
    sensorValue = random.randint(400, 600)
    current = (sensorValue - 512) * (5.0 / 1023.0) / 0.066
    power = current * voltage

    # Prepare JSON
    msg = {"current": round(current, 2), "power": round(power, 2)}
    
    # Send to ThingsBoard
    requests.post(url, json=msg)
    
    print("Sent:", msg)
    
    # Simulate delay
    time.sleep(2)