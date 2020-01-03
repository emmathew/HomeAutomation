#include <Arduino.h>
#include <ESP8266WiFi.h>

bool unconnected = true;
unsigned long unconnectedStartTimeMs = 0;
bool accessPointEnabled = false;

void tryToConnect();
void runAsAccessPoint();
void stopAccessPoint();

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(500);
  Serial.println('\n');
  Serial.println("Starting....");
  unconnectedStartTimeMs = millis();
}


void loop() {
  // put your main code here, to run repeatedly:
  tryToConnect();
  unconnected = WiFi.status() != WL_CONNECTED;
  if (unconnected && !accessPointEnabled) {
    unsigned long currentTimeMs = millis();
    unsigned long elaspedTimeMs = currentTimeMs - unconnectedStartTimeMs;
    if (elaspedTimeMs > 20000) {
      runAsAccessPoint();
    }
  }
  if (!unconnected && accessPointEnabled) {
    stopAccessPoint();
  }
  delay(100);
  
}

void runAsAccessPoint(){
  if (! accessPointEnabled) {
    Serial.println("Starting Access Point");
    const char *ssid = "MHA_Client_Access_Point"; // The name of the Wi-Fi network that will be created
    const char *password = "12341234"; 
    WiFi.softAP(ssid, password);

    Serial.print("Access Point \"");
    Serial.print(ssid);
    Serial.println("\" started");
    Serial.print("IP address:\t");
    Serial.println(WiFi.softAPIP());

    accessPointEnabled = true;
  }
}
void tryToConnect() {
  if (!accessPointEnabled) {
    Serial.println("Trying to Connect to Wifi");
    delay(1000);
    Serial.println("Failed to Connect");
  } else {
    const char* ssid     = "M &M Network Att";         // The SSID (name) of the Wi-Fi network you want to connect to
    const char* password = "12341234";     // The password of the Wi-Fi network
    WiFi.begin(ssid, password);
    Serial.print("Connecting to ");
    Serial.print(ssid); Serial.println(" ...");

    int i = 0;
    
    while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
      delay(1000);
      Serial.print(++i); Serial.print(' ');
    }

    Serial.println('\n');
    Serial.println("Connection established!");  
    Serial.print("IP address:\t");
    Serial.println(WiFi.localIP());
  }
  return;
}

void stopAccessPoint() {
  if (accessPointEnabled) {
    WiFi.softAPdisconnect();
    accessPointEnabled = false;
    Serial.println("Access Point disabled");
  }
}