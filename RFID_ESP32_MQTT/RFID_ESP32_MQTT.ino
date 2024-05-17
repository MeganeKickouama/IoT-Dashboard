#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

// WiFi credentials and MQTT server
// const char* ssid = "Big Fish";
// const char* password = "peter7435";
// const char* mqtt_server = "172.20.10.8";

const char* ssid = "Helix9354";
const char* password = "fishman7436";
const char* mqtt_server = "10.0.0.141";

// MQTT client setup
WiFiClient espClient;
PubSubClient client(espClient);

// Photoresistor pin configuration
const int photoResistorPin = 36;

// RFID configuration
#define SS_PIN 21
#define RST_PIN 22
MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

// Previous NUID
byte nuidPICC[4];

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  pinMode(photoResistorPin, INPUT);

  SPI.begin();
  rfid.PCD_Init();
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
}

// Connection to the wifi.
void setup_wifi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// Keeps looping througb the functions to keep the data up to date.
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  checkRFID();
  checkLightSensor();
  delay(1000);
}

// Checking the data for the RFID Chip, same code done in class for the lab and sending it to topic IoTLabPhase4/#
void checkRFID() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
  if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
      piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
      piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
    return;
  }

  if (memcmp(rfid.uid.uidByte, nuidPICC, 4) != 0) {
    memcpy(nuidPICC, rfid.uid.uidByte, 4);
    char hexUID[32];
    sprintf(hexUID, "Hex: %02X %02X %02X %02X", nuidPICC[0], nuidPICC[1], nuidPICC[2], nuidPICC[3]);
    client.publish("IoTLabPhase4/RFID", hexUID);
    char decUID[32];
    sprintf(decUID, "Dec: %d %d %d %d", nuidPICC[0], nuidPICC[1], nuidPICC[2], nuidPICC[3]);
    client.publish("IoTLabPhase4/RFID", decUID);
  }
  
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

// Check and get the value of the light sensor and publishes it to the topic IoTLabPhase4/#
void checkLightSensor() {
  int lightValue = analogRead(photoResistorPin);
  char payload[50];
  sprintf(payload, "Light level: %d", lightValue);
  client.publish("IoTLabPhase4/Light", payload);
}

// Whole function dedicated to reconnecting if connection is lost... Don't need to touch this it works.
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");
      client.subscribe("IoTLabPhase4/#");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
