from flask import Flask
import paho.mqtt.client as mqtt
import time, random, json, threading

app = Flask(__name__)

# ThingsBoard config
broker = "thingsboard.cloud"
access_token = "YOUR_NEW_TOKEN"

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(access_token)
client.connect(broker, 1883, 60)

def send_data():
    while True:
        voltage = round(random.uniform(220, 240), 2)
        current = round(random.uniform(0.5, 2.0), 2)
        power = round(voltage * current, 2)

        data = {
            "voltage": voltage,
            "current": current,
            "power": power
        }

        client.publish("v1/devices/me/telemetry", json.dumps(data))
        print("Sent:", data)

        time.sleep(2)

@app.route("/")
def home():
    return "IoT Device Running"

# Run MQTT in background
threading.Thread(target=send_data, daemon=True).start()

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)