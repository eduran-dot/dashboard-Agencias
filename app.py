from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json, os, urllib.request, urllib.error

app = Flask(__name__, static_folder='static')
CORS(app)

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
WRITE_TOKEN  = os.environ.get('WRITE_TOKEN', 'movicarga2026')
TABLE        = 'dashboard_data'

def headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }

def sb_get(key):
    url = f'{SUPABASE_URL}/rest/v1/{TABLE}?key=eq.{key}&select=value'
    req = urllib.request.Request(url, headers=headers())
    try:
        with urllib.request.urlopen(req) as r:
            rows = json.loads(r.read())
            return json.loads(rows[0]['value']) if rows else None
    except:
        return None

def sb_upsert(key, value):
    data = json.dumps({'key': key, 'value': json.dumps(value)}).encode()
    req = urllib.request.Request(
        f'{SUPABASE_URL}/rest/v1/{TABLE}',
        data=data, headers=headers(), method='POST'
    )
    try:
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print('Supabase error:', e)
        return False

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        'agencias':  sb_get('agencias')  or [],
        'registros': sb_get('registros') or [],
        'lpns':      sb_get('lpns')      or []
    })

@app.route('/api/data', methods=['POST'])
def save_data():
    if request.headers.get('X-Auth-Token', '') != WRITE_TOKEN:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Sin datos'}), 400
    sb_upsert('agencias',  data.get('agencias', []))
    sb_upsert('registros', data.get('registros', []))
    sb_upsert('lpns',      data.get('lpns', []))
    return jsonify({'ok': True})

@app.route('/')
def index():
    return send_from_directory('static', 'viewer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
