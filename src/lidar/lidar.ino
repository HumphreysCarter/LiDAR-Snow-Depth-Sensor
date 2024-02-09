#include <LIDARLite_v4LED.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiManager.h>

LIDARLite_v4LED LIDAR;
HTTPClient client;

const String API_SERVER = "http://10.3.14.112:7070"; // Location to send data too

const String WIFI_SSID = ""; // WiFi SSID
const String WIFI_PASSWORD = ""; // WiFi password

const int LIDAR_CONFIG = 0; // LiDAR setting 
const float LIDAR_CALIBRATION = 0.0; // Error of the LiDAR sensor

const int NUM_MEASUREMENTS = 60;  // Number of measurements to take for average
const int MEASUREMENT_INTERVAL = 1000;  // Interval between Lidar measurements in milliseconds (adjust as needed)

void setup() {
  Serial.begin(115200);
  Wire.begin();

  // Connect to WiFi
  connectToWiFi();

  // Start LiDAR
  while (LIDAR.begin() == false) {
    Serial.println("Device did not acknowledge! Freezing.");
    while (1);
    delay(MEASUREMENT_INTERVAL);
  }
  Serial.println("LIDAR acknowledged!");

  // Configure LiDAR
  LIDAR.configure(LIDAR_CONFIG);

  // Set LiDAR measurement pin
  pinMode(LED_BUILTIN, OUTPUT);
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attemptCount = 0;
  
  while (WiFi.status() != WL_CONNECTED && attemptCount < 60) {
    delay(5000);
    Serial.print(".");
    attemptCount++;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nFailed to connect to WiFi. Trying to reconnect...");
    return;
  }
  
  Serial.println("\nWiFi connected");
}

void loop() {
  // Check WiFi connection and reconnect if necessary
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Trying to reconnect...");
    connectToWiFi();
  }

  // Get average distance over the specified interval
  Serial.println("Taking measurement... ");
  int n = 0;
  float avgDistance = 0;
  
  while (n < NUM_MEASUREMENTS) {
    float d = measureDistance();
    Serial.println(String(n+1) + " of " + String(NUM_MEASUREMENTS) + " = " + String(d));
    avgDistance += d;
    delay(MEASUREMENT_INTERVAL);
    n++;
  }

  // Get average
  avgDistance /= NUM_MEASUREMENTS;
  Serial.print(avgDistance);

  // Get temperature of the board
  float boardTmp = LIDAR.getBoardTemp();

  // Send data to server
  Serial.println("Sending data to server...");
  postToServer(avgDistance, boardTmp);
}

float measureDistance() {
  float currentDistance = LIDAR.getDistance() + LIDAR_CALIBRATION;
  blinkPin();
  return currentDistance;
}

void blinkPin() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(100);
  digitalWrite(LED_BUILTIN, LOW);
}

void postToServer(float avgDistance, float boardTmp) {
  String url = API_SERVER + "/sensors/lidar/" + getNormalizedMac();
  String payload = "{\"wifi\":" + String(WiFi.RSSI())
      + ", \"average_distance\":" + String(avgDistance)
      + ", \"board_temp\":" + String(boardTmp)
      + "}";

  // Send data to server
  client.setConnectTimeout(5 * 1000);
  client.begin(url);
  client.addHeader("content-type", "application/json");
  int httpCode = client.POST(payload);
  client.end();
}

String getNormalizedMac() {
  String mac = WiFi.macAddress();
  mac.replace(":", "");
  mac.toLowerCase();
  return mac;
}