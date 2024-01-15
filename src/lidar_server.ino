#include <LIDARLite_v4LED.h>
#include <Wire.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WebServer.h>
#include <time.h>

LIDARLite_v4LED myLIDAR;

const char* ssid = ""; // WiFi SSID
const char* password = ""; // WiFi password
const char* serverName = "snow-depth-lidar";
const int serverPort = 80;

WebServer server(serverPort);

const int numMeasurements = 60;  // Number of measurements to average
float measurements[numMeasurements];
int currentIndex = 0;
unsigned long previousMillis = 0;
unsigned long interval = 1000;  // Interval between Lidar measurements in milliseconds (adjust as needed)

float averageDistanceCm = 0;

void computeAverage() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    float newDistance = myLIDAR.getDistance();

    // Store the new measurement in the array
    measurements[currentIndex] = newDistance;
    currentIndex = (currentIndex + 1) % numMeasurements;

    // Blink the LED when a new measurement is taken
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
  }

  // Calculate the average distance
  float averageDistance = 0;
  int validMeasurements = 0;

  for (int i = 0; i < numMeasurements; i++) {
    if (measurements[i] > 0) {
      averageDistance += measurements[i];
      validMeasurements++;
    }
  }

  if (validMeasurements > 0) {
    averageDistance /= validMeasurements;
  }

  // Save the computed average distance
  averageDistanceCm = averageDistance;
}

void handleRoot() {
  // Get current time in UTC
  time_t now;
  struct tm timeinfo;
  time(&now);
  gmtime_r(&now, &timeinfo);

  // Format time as a string
  char timeString[30];
  strftime(timeString, sizeof(timeString), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);

  // Create a JSON object
  String jsonData = "{\"current_distance_cm\": " + String(myLIDAR.getDistance()) +
                    ", \"average_distance_cm\": " + String(averageDistanceCm) +
                    ", \"utc_time\": \"" + String(timeString) + "\"}";

  server.send(200, "application/json", jsonData);
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (myLIDAR.begin() == false) {
    Serial.println("Device did not acknowledge! Freezing.");
    while (1);
  }
  Serial.println("LIDAR acknowledged!");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");

  configTime(0, 0, "pool.ntp.org"); // Set the NTP server

  pinMode(LED_BUILTIN, OUTPUT);  // Set the LED pin as output

  if (MDNS.begin(serverName)) {
    Serial.println("MDNS responder started");
  }

  server.on("/", HTTP_GET, handleRoot);

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  computeAverage();  // Compute the average in the background
  server.handleClient();
  delay(2);
}