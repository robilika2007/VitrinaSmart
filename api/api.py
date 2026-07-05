from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # allows the browser to call this from any origin

DB_FILE = "/app/data/sensors.db"
BOX_ID = 1


def query(sql, params=()):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def execute(sql, params=()):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()


def ensure_tables():
    execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL,
        value TEXT,
        box_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

# Runtime cache for most-recent settings (no DB persistence when using in-memory mode)
LATEST_SETTINGS = {}


@app.route("/")
def index():
    return render_template("boxPage.html")


@app.route("/data")
def get_data():
    return jsonify(query("""
        SELECT air_temp, heatpad_temp, air_humidity, soil_humidity, clean_water, dirty_water, led_power, vent_power, timestamp
        FROM sensorReadings
        WHERE box_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (BOX_ID,)))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # For now: do not persist to database. Keep settings in-memory and print them.
    global LATEST_SETTINGS
    if request.method == 'POST':
        payload = request.get_json(force=True, silent=True) or {}
        # store the payload in-memory for quick inspection
        LATEST_SETTINGS = payload
        print('Received settings POST (in-memory):', payload)
        return jsonify({'ok': True, 'received': payload})

    # GET: return the last-received payload
    return jsonify(LATEST_SETTINGS)


@app.route('/settings/view')
def settings_view():
    ensure_tables()
    rows = query('SELECT key, value, box_id, timestamp FROM settings WHERE box_id = ? ORDER BY timestamp DESC LIMIT 100', (BOX_ID,))
    # Simple HTML showing in-memory latest first (if present)
    html = ['<html><head><title>Settings</title></head><body><h1>Saved Settings</h1>']
    if LATEST_SETTINGS:
        html.append('<h2>Latest (in-memory)</h2><ul>')
        for k, v in LATEST_SETTINGS.items():
            html.append(f"<li><strong>{k}</strong>: {v}</li>")
        html.append('</ul>')

    html.append('<h2>Recent DB rows</h2><ul>')
    for r in rows:
        html.append(f"<li><strong>{r['key']}</strong>: {r['value']} <em>({r['timestamp']})</em></li>")
    html.append('</ul></body></html>')
    return Response('\n'.join(html), mimetype='text/html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)