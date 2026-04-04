from flask import Flask, jsonify, render_template_string
import paho.mqtt.client as mqtt
import time, random, json, threading, os

# Create Flask app
app = Flask(__name__)

# ThingsBoard config
ACCESS_TOKEN = "Twxv1yhVrF3fqhyzcQsy"
BROKER = "thingsboard.cloud"

# MQTT Client
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(ACCESS_TOKEN)
client.connect(BROKER, 1883, 60)
client.loop_start()  # keep alive

# Store latest data
latest_data = {"voltage": 0, "current": 0, "power": 0}

# Function to simulate and send data
def send_data():
    global latest_data
    while True:
        voltage = round(random.uniform(220, 240), 2)
        current = round(random.uniform(0.5, 2.0), 2)
        power = round(voltage * current, 2)

        latest_data = {
            "voltage": voltage,
            "current": current,
            "power": power
        }

        client.publish("v1/devices/me/telemetry", json.dumps(latest_data))
        print("Sent:", latest_data)
        time.sleep(2)

# API route to fetch data
@app.route("/data")
def data():
    return jsonify(latest_data)

# Main dashboard page
@app.route("/")
def dashboard():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Energy Monitor 🚀</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            margin: 0;
            padding: 0;
        }
        header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(to right, #00ffcc, #0055ff);
            color: #111;
            font-size: 2em;
            font-weight: bold;
        }
        .cards {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin: 20px;
        }
        .card {
            flex: 1 1 200px;
            margin: 10px;
            padding: 20px;
            border-radius: 12px;
            background: #161b22;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .card h2 {
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .value {
            font-size: 2em;
            font-weight: bold;
        }
        .green { color: #28a745; }
        .yellow { color: #ffc107; }
        .red { color: #dc3545; }
        .charts {
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }
        iframe { border: none; border-radius: 12px; width: 100%; height: 400px; }
        a { color: #00ffcc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        footer {
            text-align: center;
            padding: 15px;
            background: #111;
            color: #555;
        }
    </style>
</head>
<body onload="fetchData()">

<header>⚡ Smart Energy Monitor Dashboard</header>

<div class="cards">
    <div class="card">
        <h2>Voltage (V)</h2>
        <p id="voltage" class="value green">0</p>
    </div>
    <div class="card">
        <h2>Current (A)</h2>
        <p id="current" class="value green">0</p>
    </div>
    <div class="card">
        <h2>Power (W)</h2>
        <p id="power" class="value green">0</p>
    </div>
</div>

<div class="charts">
    <canvas id="powerChart"></canvas>
</div>

<h2 style="text-align:center;">📊 ThingsBoard Dashboard</h2>
<iframe src="https://thingsboard.cloud/dashboard/eeebd8f0-2f02-11f1-8704-2bfb9206c3d7?publicId=cb6d3d60-3010-11f1-9c6f-b71bb2771567"></iframe>

<h2 style="text-align:center;">🔗 GitHub Repository</h2>
<p style="text-align:center;"><a href="https://github.com/nakshatrameena/Smart_Home_Energy_Monitor_IoT_Project" target="_blank">View Full Project</a></p>

<footer>Made with ❤️ by Nakshatra Meena</footer>

<script>
let voltageData = [];
let currentData = [];
let powerData = [];
let labels = [];

const ctx = document.getElementById('powerChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [
            {
                label: 'Voltage (V)',
                data: voltageData,
                borderColor: '#00ffcc',
                backgroundColor: 'rgba(0,255,204,0.2)',
                fill: true,
                tension: 0.3
            },
            {
                label: 'Current (A)',
                data: currentData,
                borderColor: '#ffdd00',
                backgroundColor: 'rgba(255,221,0,0.2)',
                fill: true,
                tension: 0.3
            },
            {
                label: 'Power (W)',
                data: powerData,
                borderColor: '#ff4444',
                backgroundColor: 'rgba(255,68,68,0.2)',
                fill: true,
                tension: 0.3
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { 
                title: { display: true, text: 'Time (s)' } 
            },
            y: { 
                title: { display: true, text: 'Value' } 
            }
        }
    }
});

async function fetchData() {
    const res = await fetch('/data');
    const data = await res.json();

    document.getElementById('voltage').innerText = data.voltage;
    document.getElementById('current').innerText = data.current;
    document.getElementById('power').innerText = data.power;

    // Update color based on thresholds
    document.getElementById('voltage').className = 'value ' + (data.voltage > 235 ? 'red' : 'green');
    document.getElementById('current').className = 'value ' + (data.current > 1.5 ? 'red' : 'green');
    document.getElementById('power').className = 'value ' + (data.power > 400 ? 'red' : 'green');

    // Update chart
    const now = new Date().toLocaleTimeString();
    labels.push(now);
    voltageData.push(data.voltage);
    currentData.push(data.current);
    powerData.push(data.power);

    if (labels.length > 10) { // keep last 10 data points
        labels.shift();
        voltageData.shift();
        currentData.shift();
        powerData.shift();
    }

    chart.update();
}

setInterval(fetchData, 2000);
</script>

</body>
</html>
    """)

# Start background thread
threading.Thread(target=send_data, daemon=True).start()

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)