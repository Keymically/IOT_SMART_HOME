"""
actuator_emulator.py
Subscribes to garden/actuators/pump for commands (e.g., "ON"/"OFF") and publishes current status to garden/status/pump.
Also simulates a manual button by publishing to garden/control/manual when run with --manual flag.
"""
import argparse
import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

BROKER = "localhost"
PORT = 1883
CMD_TOPIC = "garden/actuators/pump"
STATUS_TOPIC = "garden/status/pump"
MANUAL_TOPIC = "garden/control/manual"

client = mqtt.Client("actuator_emulator")
pump_state = {"status": "OFF", "last_changed": None}

def on_connect(c, userdata, flags, rc):
    print("[ACT] Connected to broker, subscribing to cmd topic")
    c.subscribe(CMD_TOPIC)
    c.subscribe(MANUAL_TOPIC)

def on_message(c, userdata, msg):
    global pump_state
    try:
        payload = msg.payload.decode()
        print(f"[ACT] Msg on {msg.topic}: {payload}")
        if msg.topic == CMD_TOPIC:
            # expect plain "ON" / "OFF" or JSON
            if payload.strip().upper() in ("ON", "OFF"):
                pump_state["status"] = payload.strip().upper()
            else:
                # try JSON
                j = json.loads(payload)
                pump_state["status"] = j.get("command", pump_state["status"]).upper()
            pump_state["last_changed"] = datetime.now(timezone.utc).isoformat()
            publish_status()
    except Exception as e:
        print("[ACT] Error processing message:", e)

def publish_status():
    payload = {
        "status": pump_state["status"],
        "ts": datetime.now(timezone.utc).isoformat()
    }
    client.publish(STATUS_TOPIC, json.dumps(payload))
    print("[ACT] Published status:", payload)

def manual_publisher(loop_interval=15):
    # Example manual button toggling every loop_interval seconds
    while True:
        # Toggle manual intent ON briefly
        manual_payload = {"button": "PRESSED", "ts": datetime.now(timezone.utc).isoformat()}
        client.publish(MANUAL_TOPIC, json.dumps(manual_payload))
        print("[ACT] Published manual:", manual_payload)
        time.sleep(loop_interval)

def main(manual=False):
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_start()
    # publish initial status
    pump_state["last_changed"] = datetime.now(timezone.utc).isoformat()
    publish_status()
    if manual:
        manual_publisher()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", action="store_true", help="Enable manual button publisher")
    args = parser.parse_args()
    main(manual=args.manual)
