from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# ===============================
# CONFIGURATION (CHANGE THESE)
# ===============================
AUTH_URL = "https://lsg-sms-stage.land.gov.bd/api/v1/token"
SMS_URL = "https://lsg-sms-stage.land.gov.bd/api/v1/lsgsms"
USERNAME = "ldtax@lsg-stage"
PASSWORD = "9^3~!I78TF"

# ===============================
# HTML SINGLE PAGE UI
# ===============================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SMS Sender</title>

<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f8fafc, #eef2ff);
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1f2937;
    }

    .wrapper {
        display: flex;
        gap: 40px;
        align-items: center;
    }

    /* LEFT ICON AREA */
    .icon-box {
        display: none;
    }

    @media (min-width: 768px) {
        .icon-box {
            display: flex;
            align-items: center;
            justify-content: center;
            background: #2563eb;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25);
        }

        .icon-box svg {
            width: 80px;
            height: 80px;
            fill: white;
        }
    }

    /* CARD */
    .card {
        background: #ffffff;
        width: 360px;
        padding: 28px;
        border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
    }

    h2 {
        margin: 0 0 20px;
        font-size: 20px;
        font-weight: 600;
        text-align: center;
    }

    label {
        font-size: 13px;
        font-weight: 500;
        margin-top: 14px;
        display: block;
        color: #374151;
    }

    input,
    textarea {
        width: 100%;
        margin-top: 6px;
        padding: 11px 12px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    input:focus,
    textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    textarea {
        resize: none;
        min-height: 90px;
    }

    button {
        width: 100%;
        margin-top: 20px;
        padding: 12px;
        background: #2563eb;
        border: none;
        border-radius: 10px;
        color: #ffffff;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s, transform 0.1s;
    }

    button:hover {
        background: #1e40af;
    }

    button:active {
        transform: scale(0.98);
    }

    .result {
        margin-top: 14px;
        font-size: 14px;
        text-align: center;
    }
    
    .app-footer {
        position: fixed;
        bottom: 16px;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #6b7280;
        opacity: 0.9;
    }
    
    .app-footer img {
        height: 60px;
        object-fit: contain;
    }
</style>
</head>

<body>

<div class="wrapper">

    <!-- SMS ICON -->
    <div class="icon-box">
        <svg viewBox="0 0 24 24">
            <path d="M2 3h20a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H6l-4 3V4a1 1 0 0 1 1-1zm10 7L4.5 5.5h15L12 10zm0 2l8-4.5V17H4V7.5L12 12z"/>
        </svg>
    </div>

    <!-- FORM CARD -->
    <div class="card">
        <h2>Send SMS via Python</h2>

        <label>Phone Number</label>
        <input type="text" id="phone" placeholder="01XXXXXXXXX">

        <label>Message</label>
        <textarea id="message" placeholder="Type your message..."></textarea>

        <button onclick="sendSMS()">Send Message</button>

        <div class="result" id="result"></div>
    </div>

</div>

<footer class="app-footer">
    <span>কারিগরি সহায়তায় </span>
    <img src="/static/images/logomysoft-png.png" alt="Helper Logo">
</footer>

<script>
function sendSMS() {
    const phone = document.getElementById('phone').value;
    const message = document.getElementById('message').value;
    
    const phoneRegex = /^01[0-9]{9}$/;

    if (!phoneRegex.test(phone)) {
        document.getElementById('result').innerText =
            'Invalid phone number. Use 11 digits starting with 01';
        return;
    }

    fetch('/send-sms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, message })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('result').innerText = data.message || 'Done';
    })
    .catch(() => {
        document.getElementById('result').innerText = 'Error sending SMS';
    });
}
</script>

</body>
</html>
"""

# ===============================
# API FUNCTIONS
# ===============================
@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

# ===============================
# ROUTES
# ===============================
def get_auth_token():

    data = request.json
    phone = data.get("phone")
    message = data.get("message")

    payload = {
        "email": 'ldtax@lsg-stage',
        "password": "9^3~!I78TF"
    }
    # return payload["service_name"]
    # return jsonify({"message": payload})

    response = requests.post(AUTH_URL, json=payload)

    # return response.json().get("token")
    if response.status_code == 200:
        return response.json().get("token")
    return None

@app.route("/send-sms", methods=["POST"])
def send_sms():
    # return jsonify({"message": "✅test line...123"})

    data = request.json
    phone = data.get("phone")
    message = data.get("message")

    # return jsonify({"message": message})

    token = get_auth_token()
    # return jsonify({"message": "MSG: "+token})

    if not token:
        return jsonify({"message": "Authentication failed"}), 401

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "service_name": "LSG",
        "sms_type": 1,
        "sms": message + " - sent from python base.",
        "receiver_no": phone,
        "delivery_time": "2026-02-17"
    }

    response = requests.post(SMS_URL, json=payload, headers=headers)

    # return jsonify({"message": token})
    # return jsonify({"message": response.text})
    # return jsonify({"message": payload["receiver_no"]})

    if response.status_code == 200:
        return jsonify({"message": "✅ SMS sent successfully"})
    else:
        return jsonify({"message": "❌ SMS sending failed"}), 400

# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
