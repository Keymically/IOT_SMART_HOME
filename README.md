# IOT Project - Smart Garden 
A simple IoT smart garden simulation using Python, MQTT, SQLite, and Tkinter.
It demonstrates sensors, actuators, a data manager, and a GUI app working together through an MQTT broker.

## What You'll See
- Console logs from each emulator and the manager (publishing and subscribing events).
- GUI window with live updates:
    - Temperature & Humidity (from DHT)
    - Soil Moisture
    - Pump Status
    - Alerts (warnings, auto-actions, manual commands)
- Control buttons in GUI to turn the pump ON/OFF.
- Database (`smartgarden.db`) storing sensor data and alerts.

## Example Logs
- Soil Emulator:
```
[SOIL] Published: {'sensor_id': 'soil-01', 'moisture': 22, 'ts': '...'}
```

- Data Manager:
```
[DM] Soil low (22%). Publishing pump ON
[DM] Published alert: Auto: Published pump ON because soil=22%
```

- GUI Alerts:
```
WARNING: High temperature 36.5C
Auto: Published pump ON because soil=22%
GUI: Sent pump OFF
```

