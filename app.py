from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    crop = data["crop"]

    result = [
        f"Kultura: {crop}",
        "⚠️ Proveri zalivanje",
        "💧 Moguća suša",
        "🌱 Stanje srednje"
    ]

    return jsonify({
        "ndvi": 0.4,
        "advice": result
    })

import os

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
