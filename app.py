from flask import Flask, render_template, request, jsonify
import re
import math
import os  # <-- Needed for PORT from Railway

app = Flask(__name__)

def estimate_crack_time(password):
    if not password:
        return "instantly"
    
    lower = 26 if re.search(r'[a-z]', password) else 0
    upper = 26 if re.search(r'[A-Z]', password) else 0
    digits = 10 if re.search(r'\d', password) else 0
    symbols = 32 if re.search(r'[\W_]', password) else 0

    charset_size = lower + upper + digits + symbols
    if charset_size == 0:
        return "instantly"

    entropy = len(password) * math.log2(charset_size)
    seconds = (2 ** entropy) / (10 ** 12)

    intervals = [
        (31536000, "year"),
        (2592000, "month"),
        (86400, "day"),
        (3600, "hour"),
        (60, "minute"),
        (1, "second")
    ]

    for interval, name in intervals:
        if seconds >= interval:
            value = int(seconds // interval)
            return f"{value} {name}{'s' if value != 1 else ''}"

    return "instantly"

def check_strength(password):
    if not password:
        return "Very Weak", 1, ["Password cannot be empty"], "instantly"

    strength = 0
    remarks = []

    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[\W_]', password))
    length_ok = len(password) >= 8
    is_long = len(password) >= 12

    strength += 1 if length_ok else 0
    strength += 1 if has_upper else 0
    strength += 1 if has_lower else 0
    strength += 1 if has_digit else 0
    strength += 1 if has_special else 0
    strength += 1 if is_long else 0

    if strength >= 5:
        rating = "Very Strong"
    elif strength >= 4:
        rating = "Strong"
    elif strength >= 3:
        rating = "Medium"
        if not has_upper:
            remarks.append("Add uppercase letters")
        if not has_special:
            remarks.append("Add special characters")
        if not is_long:
            remarks.append("Make it longer (12+ characters)")
    else:
        rating = "Weak" if strength >= 2 else "Very Weak"
        if not length_ok:
            remarks.append("At least 8 characters")
        if not has_upper:
            remarks.append("Add uppercase letters")
        if not has_lower:
            remarks.append("Add lowercase letters")
        if not has_digit:
            remarks.append("Add numbers")
        if not has_special:
            remarks.append("Add special characters")

    meter_strength = min(max(strength, 1), 5)
    crack_time = estimate_crack_time(password)

    return rating, meter_strength, remarks[:3], crack_time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    password = data.get('password', '')
    rating, strength, remarks, crack_time = check_strength(password)
    return jsonify({
        'rating': rating,
        'strength': strength,
        'remarks': remarks,
        'crack_time': crack_time
    })

# ✅ THIS FIXES RAILWAY ACCESS

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

