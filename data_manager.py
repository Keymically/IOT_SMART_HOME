"""
data_manager.py
- Subscribes to all sensor topics
- Writes readings to local SQLite
- Implements simple automation: if soil < threshold -> publish ON to pump actuator
- Publishes warnings (e.g., temp too high) to garden/alerts
"""
import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

TOPICS = [
    ("garden/sensors/dht", 0),
    ("garden/sensors/soil", 0),
    ("garden/control/manual", 0),   # listen to manual button
]

ACTUATOR_CMD_TOPIC = "garden/actuators/pump"
ALERTS_TOPIC = "garden/alerts"
PUMP_STATUS_TOPIC = "garden/status/pump"

DB_FILE = "smartgarden.db"
SOIL_THRESHOLD = 30  # percent
TEMP_WARNING = 35.0  # deg C

client = mqtt.Client("data_manager")

# --- Database helpers ---
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            topic TEXT,
            payload TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            alert TEXT
        )
    """)
    conn.commit()
    return conn

db_conn = init_db()
db_lock = threading.Lock()

def save_sensor(topic, payload_json):
    with db_lock:
        cur = db_conn.cursor()
        cur.execute("INSERT INTO sensor_data (ts, topic, payload) VALUES (?, ?, ?)",
                    (datetime.now(timezone.utc).isoformat(), topic, json.dumps(payload_json)))
        db_conn.commit()

def save_alert(text):
    with db_lock:
        cur = db_conn.cursor()
        cur.execute("INSERT INTO alerts (ts, alert) VALUES (?, ?)",
                    (datetime.now(timezone.utc).isoformat(), text))
        db_conn.commit()

# --- Automation logic ---
def handle_dht(payload):
    # payload expected with keys "temp" and "hum"
    temp = payload.get("temp")
    if temp is not None and isinstance(temp, (int, float)):
        if temp > TEMP_WARNING:
            alert_text = f"WARNING: High temperature {temp}C"
            client.publish(ALERTS_TOPIC, alert_text)
            save_alert(alert_text)
            print("[DM] Published alert:", alert_text)

def handle_soil(payload):
    moisture = payload.get("moisture")
    if moisture is not None:
        if moisture < SOIL_THRESHOLD:
            # send ON command to pump
            cmd = "ON"
            client.publish(ACTUATOR_CMD_TOPIC, cmd)
            print(f"[DM] Soil low ({moisture}%). Publishing pump {cmd}")
            save_alert(f"Auto: Published pump {cmd} because soil={moisture}%")
        else:
            # optionally turn pump off
            cmd = "OFF"
            client.publish(ACTUATOR_CMD_TOPIC, cmd)
            print(f"[DM] Soil ok ({moisture}%). Publishing pump {cmd}")

def on_connect(c, userdata, flags, rc):
    print("[DM] Connected to MQTT broker. Subscribing to topics...")
    for t, qos in TOPICS:
        c.subscribe(t, qos=qos)

def on_message(c, userdata, msg):
    try:
        payload = msg.payload.decode()
        # try parse JSON else keep as raw
        try:
            data = json.loads(payload)
        except Exception:
            data = {"raw": payload}
        print(f"[DM] Msg on {msg.topic}: {data}")
        save_sensor(msg.topic, data)

        # route to logic
        if msg.topic == "garden/sensors/dht":
            handle_dht(data)
        elif msg.topic == "garden/sensors/soil":
            handle_soil(data)
        elif msg.topic == "garden/control/manual":
            # manual control pressed -> toggle pump maybe
            save_alert("Manual control event received")
            client.publish(ACTUATOR_CMD_TOPIC, "ON")
    except Exception as e:
        print("[DM] Error processing message:", e)

def main():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

if __name__ == "__main__":
    main()
