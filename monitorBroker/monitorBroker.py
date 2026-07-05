import paho.mqtt.client as mqtt
import json
import sqlite3

BROKER_HOST = "mosquitto"
BROKER_PORT = 1883
TOPIC       = "sensors/+"
DB_FILE = "/app/data/sensors.db"

ALLOWED_SENSORS = {"air_temp", "heatpad_temp", "air_humidity", "soil_humidity", "clean_water", "dirty_water", "led_power", "vent_power"}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to {TOPIC}")
    else:
        print(f"Connection failed, code: {reason_code}")


def on_message(client, userdata, msg):
    parts = msg.topic.split("/")

    if len(parts) != 2 or parts[0] != "sensors" or not parts[1]:
        print(f"Invalid topic format: {msg.topic} — expected sensors/<boxID>")
        return

    box_id = parts[1]

    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"Invalid JSON payload on {msg.topic}: {msg.payload}")
        return

    if not isinstance(data, dict):
        print(f"Payload must be a JSON object, got: {data}")
        return

    conn = sqlite3.connect(DB_FILE)
    air_temp = data.get("air_temp")
    heatpad_temp = data.get("heatpad_temp")
    air_humidity = data.get("air_humidity")
    soil_humidity = data.get("soil_humidity")
    clean_water = data.get("clean_water")
    dirty_water = data.get("dirty_water")
    led_power = data.get("led_power")
    vent_power = data.get("vent_power")

    if all(value is None for value in [air_temp, heatpad_temp, air_humidity, soil_humidity, clean_water, dirty_water, led_power, vent_power]):
        print(f"No supported sensor readings in payload for {msg.topic}")
        conn.close()
        return

    conn.execute(
        "INSERT INTO sensorReadings (box_id, air_temp, heatpad_temp, air_humidity, soil_humidity, clean_water, dirty_water, led_power, vent_power) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (box_id, air_temp, heatpad_temp, air_humidity, soil_humidity, clean_water, dirty_water, led_power, vent_power)
    )
    print(f"  [{box_id}] air_temp={air_temp}, heatpad_temp={heatpad_temp}, air_humidity={air_humidity}, soil_humidity={soil_humidity}, clean_water={clean_water}, dirty_water={dirty_water}, led_power={led_power}, vent_power={vent_power}")

    conn.commit()
    conn.close()


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_HOST, BROKER_PORT)
client.loop_forever()