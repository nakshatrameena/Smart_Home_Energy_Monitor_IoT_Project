#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";

// MQTT Broker (ThingsBoard)
const char* mqtt_server = "demo.thingsboard.io";
const int mqtt_port = 1883;
const char* access_token = "YOUR_DEVICE_ACCESS_TOKEN";

WiFiClient espClient;
PubSubClient client(espClient);

// Pins
const int currentSensorPin = A0;
const int relayPin = 5;
const int ledPin = 4;

float voltage = 230.0; // AC mains voltage
float powerThreshold = 2000; // Threshold in watts

void setup() {
  Serial.begin(115200);
  pinMode(relayPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void setup_wifi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected!");
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  int sensorValue = analogRead(currentSensorPin);
  float current = (sensorValue - 512) * (5.0 / 1023.0) / 0.066;
  float power = current * voltage;

  Serial.print("Current: "); Serial.print(current); Serial.print(" A, ");
  Serial.print("Power: "); Serial.print(power); Serial.println(" W");

  char msg[100];
  sprintf(msg, "{\"current\": %.2f, \"power\": %.2f}", current, power);
  client.publish("v1/devices/me/telemetry", msg);

  if (power > powerThreshold) {
    digitalWrite(ledPin, HIGH);
    digitalWrite(relayPin, LOW);
  } else {
    digitalWrite(ledPin, LOW);
    digitalWrite(relayPin, HIGH);
  }

  delay(2000);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32Client", access_token, NULL)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}