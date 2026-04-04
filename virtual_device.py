from flask import Flask, jsonify, render_template_string
import paho.mqtt.client as mqtt
import time, random, json, threading, os

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)

# -----------------------------
# ThingsBoard Config
# -----------------------------
BROKER = "thingsboard.cloud"
ACCESS_TOKEN = "Twxv1yhVrF3fqhyzcQsy"

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(ACCESS_TOKEN)
client.connect(BROKER, 1883, 60)
client.loop_start()  # Important for MQTT background loop

# -----------------------------
# Telemetry & Alerts Config
# -----------------------------
latest_data = {"voltage": 0, "current": 0, "power": 0, "alert": ""}

# Set alert thresholds
THRESHOLDS = {
    "voltage": {"min": 210, "max": 240},
    "current": {"max": 2.0},
    "power": {"max": 400}
}

def check_alerts(voltage, current, power):
    alerts = []
    if voltage < THRESHOLDS["voltage"]["min"] or voltage > THRESHOLDS["voltage"]["max"]:
        alerts.append(f"Voltage out of range: {voltage}V")
    if current > THRESHOLDS["current"]["max"]:
        alerts.append(f"Current too high: {current}A")
    if power > THRESHOLDS["power"]["max"]:
        alerts.append(f"Power overload: {power}W")
    return ", ".join(alerts)

# -----------------------------
# Function to send data
# -----------------------------
def send_data():
    global latest_data
    while True:
        voltage = round(random.uniform(220, 240), 2)
        current = round(random.uniform(0.5, 2.0), 2)
        power = round(voltage * current, 2)
        alert_msg = check_alerts(voltage, current, power)

        latest_data = {
            "voltage": voltage,
            "current": current,
            "power": power,
            "alert": alert_msg
        }

        # Publish telemetry
        client.publish("v1/devices/me/telemetry", json.dumps(latest_data))
        print("Sent:", latest_data)

        # Publish alarm if exists
        if alert_msg:
            client.publish("v1/devices/me/attributes", json.dumps({"alert": alert_msg}))
            print("⚠ Alert sent:", alert_msg)

        time.sleep(2)

# -----------------------------
# Flask API Routes
# -----------------------------
@app.route("/data")
def data():
    return jsonify(latest_data)

@app.route("/")
def dashboard():
    return render_template_string("""
<html>
<head>
<title>Smart Energy Monitor</title>
<script>
async function fetchData() {
    const res = await fetch('/data');
    const data = await res.json();
    document.getElementById('voltage').innerText = data.voltage;
    document.getElementById('current').innerText = data.current;
    document.getElementById('power').innerText = data.power;
    document.getElementById('alert').innerText = data.alert || "No alerts";
}
setInterval(fetchData, 2000);
</script>
<style>
body { font-family: Arial; background: #111; color: #fff; text-align: center; }
.card { display: inline-block; padding: 20px; margin: 15px; border-radius: 10px; background: #222; }
iframe { border: none; border-radius: 10px; }
pre { text-align: left; background: #000; padding: 15px; overflow-x: auto; }
h1 { color: #00ffcc; }
a { color: #00ffcc; }
</style>
</head>
<body onload="fetchData()">

<h1>⚡ Smart Energy Monitor Dashboard</h1>

<div class="card">
<h2>Voltage (V)</h2>
<p id="voltage">0</p>
</div>

<div class="card">
<h2>Current (A)</h2>
<p id="current">0</p>
</div>

<div class="card">
<h2>Power (W)</h2>
<p id="power">0</p>
</div>

<div class="card">
<h2>Alerts</h2>
<p id="alert">No alerts</p>
</div>

<h2>📊 Cloud Dashboard</h2>
<a href="https://thingsboard.cloud/dashboard/eeebd8f0-2f02-11f1-8704-2bfb9206c3d7?publicId=cb6d3d60-3010-11f1-9c6f-b71bb2771567" target="_blank">
Open ThingsBoard Dashboard
</a>

<h2>🔗 GitHub Repository</h2>
<a href="https://github.com/nakshatrameena/Smart_Home_Energy_Monitor_IoT_Project" target="_blank">
View Project on GitHub
</a>

</body>
</html>
""")

# -----------------------------
# Start background thread
# -----------------------------
threading.Thread(target=send_data, daemon=True).start()

# -----------------------------
# Run Flask App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)