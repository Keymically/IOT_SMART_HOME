@echo off
REM Start all smart garden emulators

echo Starting Actuator Emulator...
start cmd /k "python actuator_emulator.py --manual"

echo Starting Soil Emulator...
start cmd /k "python soil_emulator.py"

echo Starting DHT Emulator...
start cmd /k "python dht_emulator.py"

echo All emulators started.
pause


@REM // arg: Name Units Place UpdateTime

@REM start "Emulator: DHT-1" python emulator.py DHT-1 Celsius Room_1 7  
@REM timeout 3 
@REM start "Emulator: DHT-2" python emulator.py DHT-2 Celsius Common 11
@REM timeout 3
@REM start "Emulator: Electricity&Water Meter" python emulator.py ElecWaterMeter kWh Home 13
@REM timeout 3
@REM start "Emulator: Airconditioner" python emulator.py Airconditioner Celsius air-1 5
@REM timeout 3
@REM start "Emulator: Freezer" python emulator.py Freezer Celsius freezer 6
@REM timeout 3
@REM start "Emulator: Boiler" python emulator.py Boiler Celsius boiler 8
@REM timeout 3
@REM start "Emulator: Refrigerator" python emulator.py Refrigerator Celsius refrigerator 9
@REM timeout 3
@REM start "Smart Home Manager" python manager.py
@REM timeout 10
@REM start "System GUI" python gui.py