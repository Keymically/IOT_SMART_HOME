"""
gui_app.py
Simple Tkinter GUI:
- Shows latest temperature, humidity, soil moisture, pump status
- Shows a listbox of alerts (subscribes to garden/alerts)
- Manual ON/OFF buttons to control pump (publishes to garden/actuators/pump)
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

SENSOR_TOPICS = [("garden/sensors/dht", 0), ("garden/sensors/soil", 0), ("garden/status/pump", 0), ("garden/alerts", 0)]

class App:
    def __init__(self, root):
        self.root = root
        root.title("Smart Garden GUI")

        frm = ttk.Frame(root, padding=10)
        frm.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Labels
        self.temp_var = tk.StringVar(value="--")
        self.hum_var = tk.StringVar(value="--")
        self.soil_var = tk.StringVar(value="--")
        self.pump_var = tk.StringVar(value="--")

        ttk.Label(frm, text="Temperature:").grid(column=0, row=0, sticky="w")
        ttk.Label(frm, textvariable=self.temp_var).grid(column=1, row=0, sticky="w")
        ttk.Label(frm, text="Humidity:").grid(column=0, row=1, sticky="w")
        ttk.Label(frm, textvariable=self.hum_var).grid(column=1, row=1, sticky="w")
        ttk.Label(frm, text="Soil Moisture:").grid(column=0, row=2, sticky="w")
        ttk.Label(frm, textvariable=self.soil_var).grid(column=1, row=2, sticky="w")
        ttk.Label(frm, text="Pump Status:").grid(column=0, row=3, sticky="w")
        ttk.Label(frm, textvariable=self.pump_var).grid(column=1, row=3, sticky="w")

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(column=0, row=4, columnspan=2, pady=(10,0))
        ttk.Button(btn_frame, text="Pump ON", command=lambda: self.publish_cmd("ON")).grid(column=0, row=0, padx=5)
        ttk.Button(btn_frame, text="Pump OFF", command=lambda: self.publish_cmd("OFF")).grid(column=1, row=0, padx=5)

        # Alerts
        ttk.Label(frm, text="Alerts:").grid(column=0, row=5, sticky="w", pady=(10,0))
        self.alert_box = scrolledtext.ScrolledText(frm, height=8, width=50, state="disabled")
        self.alert_box.grid(column=0, row=6, columnspan=2, sticky="nsew")

        # MQTT client in background thread
        self.mqtt_client = mqtt.Client("gui_app")
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(BROKER, PORT)
        threading.Thread(target=self.mqtt_client.loop_forever, daemon=True).start()

    def on_connect(self, client, userdata, flags, rc):
        for t, qos in SENSOR_TOPICS:
            client.subscribe(t)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        try:
            j = json.loads(payload)
        except Exception:
            j = payload
        # Update UI in main thread
        self.root.after(0, self.handle_msg_on_ui_thread, msg.topic, j)

    def handle_msg_on_ui_thread(self, topic, data):
        if topic == "garden/sensors/dht":
            if isinstance(data, dict):
                self.temp_var.set(f"{data.get('temp', '--')} °C")
                self.hum_var.set(f"{data.get('hum', '--')} %")
        elif topic == "garden/sensors/soil":
            if isinstance(data, dict):
                self.soil_var.set(f"{data.get('moisture', '--')} %")
        elif topic == "garden/status/pump":
            if isinstance(data, dict):
                self.pump_var.set(data.get("status", "--"))
        elif topic == "garden/alerts":
            # append alert text
            alert_text = data if isinstance(data, str) else json.dumps(data)
            self.alert_box.configure(state="normal")
            self.alert_box.insert("end", f"{alert_text}\n")
            self.alert_box.configure(state="disabled")
            # auto-scroll
            self.alert_box.see("end")

    def publish_cmd(self, cmd):
        self.mqtt_client.publish("garden/actuators/pump", cmd)
        # Also show in UI
        self.alert_box.configure(state="normal")
        self.alert_box.insert("end", f"GUI: Sent pump {cmd}\n")
        self.alert_box.configure(state="disabled")
        self.alert_box.see("end")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
