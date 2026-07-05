import sqlite3

DB_FILE = "/app/data/sensors.db"

conn = sqlite3.connect(DB_FILE)

conn.execute("""
    CREATE TABLE IF NOT EXISTS sensorReadings (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        box_id    INTEGER,
        air_temp     REAL,
        heatpad_temp REAL,
        air_humidity   REAL,
        soil_humidity  REAL,
        clean_water REAL,
        dirty_water REAL,
        led_power REAL,
        vent_power REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()

print("Database ready.")