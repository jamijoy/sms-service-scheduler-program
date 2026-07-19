from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import requests
import json
import os

app = Flask(__name__)
#need to check time
CORS(app)  # allow all origins

# ===============================
# CONFIGURATION (CHANGE THESE)
# ===============================
AUTH_URL = "https://lsg-sms-stage.land.gov.bd/api/v1/token"
SMS_URL = "https://lsg-sms-stage.land.gov.bd/api/v1/lsgsms"
USERNAME = "ldtax@lsg-stage"
PASSWORD = "9^3~!I78TF"
FILE_PATH = "data-contact-form.json"

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

# Small built-in test page so you can try the endpoint without Postman
TEST_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Sales Prediction Tester</title>
  <style>
    body { font-family: sans-serif; max-width: 700px; margin: 40px auto; }
    textarea { width: 100%; height: 160px; font-family: monospace; }
    button { padding: 8px 16px; margin-top: 10px; cursor: pointer; }
    pre { background: #f4f4f4; padding: 12px; overflow-x: auto; }
  </style>
</head>
<body>
  <h2>Sales Prediction Tester</h2>
  <p>Edit the JSON below and click Predict.</p>
  <textarea id="input">{
  "historical_data": [
    {"date": "2026-06-01", "sales": 1000},
    {"date": "2026-06-02", "sales": 1050},
    {"date": "2026-06-03", "sales": 1020},
    {"date": "2026-06-04", "sales": 1100},
    {"date": "2026-06-05", "sales": 1180},
    {"date": "2026-06-06", "sales": 1150},
    {"date": "2026-06-07", "sales": 1220}
  ],
  "periods_ahead": 7,
  "method": "linear"
}</textarea>
  <br>
  <button onclick="runPredict()">Predict</button>
  <h3>Result</h3>
  <pre id="output">(no result yet)</pre>
 
  <script>
    async function runPredict() {
      const out = document.getElementById('output');
      out.textContent = 'Loading...';
      try {
        const body = JSON.parse(document.getElementById('input').value);
        const res = await fetch('/api/predict-sales', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        out.textContent = 'Error: ' + e.message;
      }
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

@app.route("/test-page", methods=["GET"])
def index():
    return render_template_string(TEST_PAGE)

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
        return jsonify({"message": response}), 400

@app.route('/test', methods=["GET"])
def test_func():
    return jsonify({"message": "Hello Render World!"}), 400

@app.route('/save-contact-form', methods=["POST"])
def save_contact_form():

    data = request.json

    new_entry = {
        "name": data.get("name"),
        "email": data.get("email"),
        "subject": data.get("subject"),
        "message": data.get("message"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Step 1: Read existing data
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Step 2: Append new data
    existing_data.append(new_entry)

    # Step 3: Save back to file
    with open(FILE_PATH, "w") as file:
        json.dump(existing_data, file, indent=4)

    return jsonify({"message": "Data saved successfully at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


@app.route('/show-saved-contact-message', methods=["GET"])
def show_saved_feedbacks():

    # Step 1: Read existing data
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    return jsonify({"Saved Data": existing_data})


def _parse_date(value):
    """Accepts 'YYYY-MM-DD' strings or datetime objects."""
    if isinstance(value, datetime):
        return value
    return datetime.strptime(value, "%Y-%m-%d")


def predict_sales(historical_data, periods_ahead=7, method="linear"):
    """
    historical_data: list of {"date": "YYYY-MM-DD", "sales": number}, sorted or not.
    periods_ahead: how many future periods (days) to predict.
    method: "linear" (trend line) or "moving_average" (last-N average, flat forecast).

    Returns a dict with historical echo, predictions, and basic model info.
    """
    if not historical_data or len(historical_data) < 2:
        raise ValueError("Need at least 2 historical data points to predict.")

    # Sort by date and pull out arrays
    rows = sorted(historical_data, key=lambda r: _parse_date(r["date"]))
    dates = [_parse_date(r["date"]) for r in rows]
    sales = np.array([float(r["sales"]) for r in rows])

    # Use day-offsets from the first date as the x-axis so gaps in dates are handled correctly
    x = np.array([(d - dates[0]).days for d in dates], dtype=float)

    last_date = dates[-1]
    future_offsets = np.array([
        (last_date - dates[0]).days + i
        for i in range(1, periods_ahead + 1)
    ], dtype=float)
    future_dates = [last_date + timedelta(days=i) for i in range(1, periods_ahead + 1)]

    if method == "moving_average":
        window = min(7, len(sales))
        avg = float(np.mean(sales[-window:]))
        predictions = [avg] * periods_ahead
        model_info = {"method": "moving_average", "window": window}

    else:  # linear regression trend
        # degree-1 polyfit: sales = slope * x + intercept
        slope, intercept = np.polyfit(x, sales, 1)
        predictions = (slope * future_offsets + intercept).tolist()
        # never predict negative sales
        predictions = [max(0, round(p, 2)) for p in predictions]

        # simple R^2 for a sense of fit quality
        fitted = slope * x + intercept
        ss_res = float(np.sum((sales - fitted) ** 2))
        ss_tot = float(np.sum((sales - np.mean(sales)) ** 2))
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

        model_info = {
            "method": "linear",
            "slope_per_day": round(float(slope), 4),
            "intercept": round(float(intercept), 4),
            "r_squared": round(r_squared, 4),
        }

    return {
        "historical": [
            {"date": d.strftime("%Y-%m-%d"), "sales": float(s)}
            for d, s in zip(dates, sales)
        ],
        "predictions": [
            {"date": d.strftime("%Y-%m-%d"), "predicted_sales": round(p, 2)}
            for d, p in zip(future_dates, predictions)
        ],
        "model_info": model_info,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/predict-sales", methods=["POST"])
def api_predict_sales():
    """
    Expected JSON body:
    {
        "historical_data": [{"date": "2026-01-01", "sales": 1000}, ...],
        "periods_ahead": 7,
        "method": "linear"   # or "moving_average"
    }
    """
    body = request.get_json(silent=True)
    return jsonify(body), 500         # test line

    if not body or "historical_data" not in body:
        return jsonify({"error": "Missing 'historical_data' in request body."}), 400

    periods_ahead = int(body.get("periods_ahead", 7))
    method = body.get("method", "linear")

    if method not in ("linear", "moving_average"):
        return jsonify({"error": "method must be 'linear' or 'moving_average'."}), 400

    try:
        result = predict_sales(body["historical_data"], periods_ahead, method)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})



# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
