"""
soil_emulator.py
Publishes soil moisture every X seconds to topic: garden/sensors/soil
Payload: JSON {"moisture": int, "sensor_id":"soil-01", "ts": "ISO8601"}
"""
import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

BROKER = "localhost"
PORT = 1883
TOPIC = "garden/sensors/soil"
PUBLISH_INTERVAL = 7

client = mqtt.Client("soil_emulator")

def main():
    client.connect(BROKER, PORT)
    client.loop_start()
    while True:
        moisture = random.randint(15, 80)  # percentage
        payload = {
            "sensor_id": "soil-01",
            "moisture": moisture,
            "ts": datetime.now(timezone.utc).isoformat()
        }
        client.publish(TOPIC, json.dumps(payload))
        print(f"[SOIL] Published: {payload}")
        time.sleep(PUBLISH_INTERVAL)

if __name__ == "__main__":
    main()
