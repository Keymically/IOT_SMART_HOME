"""
dht_emulator.py
Publishes temperature & humidity periodically to topic: garden/sensors/dht
Payload: JSON {"temp": float, "hum": float, "sensor_id": "dht-01", "ts": "ISO8601"}
"""
import time
import json
import random
import threading
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

BROKER = "localhost"
PORT = 1883
TOPIC = "garden/sensors/dht"
PUBLISH_INTERVAL = 5  # seconds

client = mqtt.Client("dht_emulator")

def publish_loop():
    while True:
        temp = round(random.uniform(18.0, 30.0), 2)  # simulate
        hum = round(random.uniform(30.0, 70.0), 2)
        payload = {
            "sensor_id": "dht-01",
            "temp": temp,
            "hum": hum,
            "ts": datetime.now(timezone.utc).isoformat()
        }
        client.publish(TOPIC, json.dumps(payload))
        print(f"[DHT] Published: {payload}")
        time.sleep(PUBLISH_INTERVAL)

def main():
    client.connect(BROKER, PORT)
    client.loop_start()
    publish_loop()

if __name__ == "__main__":
    main()
